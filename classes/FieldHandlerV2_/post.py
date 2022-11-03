def post(self):
    import base64
    is_utah = ( (self.request.get("cust_state").upper() == "UT") or (self.request.get("cust_state").upper() == "UTAH") )
    is_texas = ( (self.request.get("cust_state").upper() == "TX") or (self.request.get("cust_state").upper() == "TEXAS") )
    #self.session = get_current_session()
    tyme = int(time.time() * 1000)

    c_email = str(self.request.get("cust_email"))
    if len(c_email.strip()) == 0:
        c_email = "didnt_want_to_provide_email@no_domain.com"

    pic_ext = "jpg"
    new_id = Helpers.guid()
    if str(self.request.get("has_qual_card")) == "1":
        file_content = self.request.POST.multi['pic'].file.read()
        file_content_b64 = base64.b64encode(file_content)        
        pic_name = self.request.params["pic"].filename.lower()
        name_elements = pic_name.split(".")
        pic_type = name_elements[len(name_elements) - 1]
        pic_mime = self.request.POST['pic'].type        
        if "png" in pic_mime.lower():
            pic_ext = "png"

        bucket_name = os.environ.get('BUCKET_NAME',
                                app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        filename = bucket + '/QualificationCards/' + new_id + "." + pic_ext

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(filename,
                            'w',
                            content_type=pic_mime,
                            options={'x-goog-meta-foo': 'foo',
                                    'x-goog-meta-bar': 'bar',
                                    'x-goog-acl': 'public-read'},
                            retry_params=write_retry_params)
        gcs_file.write(file_content)
        gcs_file.close()

    #pic_name2 = self.request.params["pic2"].filename.lower()
    #name_elements2 = pic_name2.split(".")
    #pic_type2 = name_elements2[len(name_elements2) - 1]
    #file_content2 = self.request.POST.multi['pic2'].file.read()
    #pic_ext2 = ""
    #pic_mime2 = ""
    #if pic_type2 == "png":
        #pic_ext2 = "png"
        #pic_mime2 = "image/png"
    #else:
        #pic_ext2 = "jpg"
        #pic_mime2 = "image/jpg"

    #filename2 = bucket + '/UtilityBills/' + new_id + "." + pic_ext2
    #gcs_file2 = gcs.open(filename2,
                         #'w',
                         #content_type=pic_mime2,
                         #options={'x-goog-meta-foo': 'foo',
                                  #'x-goog-meta-bar': 'bar',
                                  #'x-goog-acl': 'public-read'},
                         #retry_params=write_retry_params)

    #gcs_file2.write(file_content2)
    #gcs_file2.close()

    field_app_id = new_id

    appt_date_items = self.request.get("cust_appointment_date").split("-")
    fixed_name = self.request.get("cust_first")[0].upper() + self.request.get("cust_first")[1:] + " " + self.request.get("cust_last")[0].upper() + self.request.get("cust_last")[1:]
    #create the survey booking
    booking = SurveyBooking(
        identifier=Helpers.guid(),
        office_identifier=self.request.get("rep_office"),
        field_app_identifier=field_app_id,
        field_app_lead_id=self.request.get("lead_id_real"),
        has_associated_field_entry=True,
        slot_number=1,
        booking_day=1,
        booking_month=1,
        booking_year=1970,
        address=self.request.get("cust_address"),
        city=self.request.get("cust_city"),
        state=self.request.get("cust_state"),
        postal=self.request.get("cust_postal"),
        phone_number=self.request.get("cust_phone"),
        email=c_email,
        name=fixed_name,
        completion_state=0,
        associated_rep_id=self.request.get("rep_id").upper(),
        utility_no=self.request.get("cust_utility_account_no"),
        notes="",
        fund="n/a",
        trust_docs="n/a",
        utility_provider=self.request.get("cust_utility_provider"),
	    archived=False,
        save_me=False,
        funding_tier="n/a"
    )
    #if str(self.request.get("is_cash")) == "1":
    #    booking.fund = "cash"

    success = True
    ##
    ##
    if success:
        booking.put()

        sig_date_items = self.request.get("cust_signature_date").split("-")
        sig_date = date(
            int(sig_date_items[2]),
            int(sig_date_items[0]),
            int(sig_date_items[1])
        )

        #dob_date_items = self.request.get("cust_dob").split("-")
        #dob_date = date(
            #int(dob_date_items[2]),
            #int(dob_date_items[0]),
            #int(dob_date_items[1])
        #)

        new_sp2_items = self.request.get("sp2_mom").split(" ")
        new_sp2_dt_vals = new_sp2_items[0].split("-")
        new_sp2_time_vals = new_sp2_items[1].split(":")

        new_sp2 = datetime(int(new_sp2_dt_vals[0]), int(new_sp2_dt_vals[1]), int(new_sp2_dt_vals[2]), int(new_sp2_time_vals[0]), int(new_sp2_time_vals[1]))

        generator = "-1"
        is_processed = True
        create_lead = True
        lead_value = False
        if str(self.request.get("user_type")) in ["solar_pro", "solar_pro_manager"]:
            generator = self.request.get("user_identifier")
            is_processed = False
            create_lead = False
            lead_value = True

        app_entry = FieldApplicationEntry(
            identifier=field_app_id,
            office_identifier=self.request.get("rep_office"),
            booking_identifier=booking.identifier,
            customer_signature_date=sig_date,
            customer_first_name=self.request.get("cust_first")[0].upper() + self.request.get("cust_first")[1:],
            customer_last_name=self.request.get("cust_last")[0].upper() + self.request.get("cust_last")[1:],
            customer_email=c_email.lower(),
            customer_phone=self.request.get("cust_phone"),
            customer_dob=date(1800, 1, 1),
            customer_postal=self.request.get("cust_postal"),
            customer_city=self.request.get("cust_city"),
            customer_state=self.request.get("cust_state"),
            customer_county=self.request.get("cust_county"),
            customer_address=self.request.get("cust_address"),
            customer_cpf_id=-1,
            customer_utility_account_number=self.request.get("cust_utility_account_no"),
            customer_kwh_price="-1.0",
            rep_id=self.request.get("rep_id"),
            rep_email=self.request.get("rep_email"),
            rep_phone=self.request.get("rep_phone"),
            rep_lead_id=self.request.get("lead_id_real"),
            insert_time=tyme,
            processed=is_processed,
            image_extension=pic_ext,
            opt_rep_notes=self.request.get("notes_for_surveyor"),
            sp_two_time = new_sp2,
            utility_provider=self.request.get("cust_utility_provider"),
            customer_mosaic_id=-1,
	        archived=False,
	        archive_reason="n/a",
            has_holds=False,
            hold_items="[]",
            save_me=False,
            save_me_reason="n/a",
            save_me_dt=datetime(1970, 1, 1),
            spouse_name="n/a",
            hide_from_recent_view=False,
            usage_info_available=(self.request.get("got_usage") == "1"),
            usage_months=0,
            total_kwhs=float(0),
            total_dollars=float(0),
            highest_amount=float(0),
            proposal_state=0,
            tier_option="A",
            deal_closed=False,
            new_survey_state=0,
            usage_data="{}",
            deal_locked=False,
            baseline_price=-1.0,
            is_lead=lead_value,
            lead_generator=generator
        )
        if app_entry.spouse_name.strip() == "":
            app_entry.spouse_name = "n/a"

        if app_entry.is_lead == True:
            notification = Notification.first(Notification.action_name == "New Solar Pro Lead")
            if not notification is None:
                msg = "There is a new lead waiting to be assigned."
                for p in notification.notification_list:
                    #Helpers.send_email(p.email_address, "New Lead", msg)
                    x = 5

        #kv_item5 = KeyValueStoreItem(
        #    identifier=Helpers.guid(),
        #    keyy=app_entry.identifier + "_spouse",
        #    val=self.request.get("spouse_name"),
        #    expiration=datetime(1970, 1, 1)
        #)
        #kv_item5.put()


        real_or_estimated_kv_val = "real"
        if str(self.request.get("real_or_estimated_value")) == "estimated":
            real_or_estimated_kv_val = "estimated"
        real_or_estimated_kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="real_or_estimated_" + app_entry.identifier,
            val=real_or_estimated_kv_val,
            expiration=datetime(1970, 1, 1)
        )
        real_or_estimated_kv.put()

        original_kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="original_real_or_estimated_" + app_entry.identifier,
            val=real_or_estimated_kv.val,
            expiration=datetime(1970, 1, 1)
        )
        original_kv.put()

        if str(self.request.get("amigo")) == "1":
            amigo_stat = LeaderBoardStat(
                identifier=Helpers.guid(),
                rep_id=app_entry.rep_id,
                dt=Helpers.pacific_now(),
                metric_key="leads_acquired_amigo",
                office_identifier=app_entry.office_identifier,
                field_app_identifier=app_entry.identifier,
                in_bounds=True,
                pin_identifier="-1"
            )
            amigo_stat.put()
            
                


        #create the document indent
        data_item = {}
        data_item["identifier"] = app_entry.identifier
        data_item["first_name"] = app_entry.customer_first_name
        data_item["last_name"] = app_entry.customer_last_name
        data_item["spouse"] = app_entry.spouse_name
        data_item["spouse_name"] = app_entry.spouse_name
        data_item["rep_id"] = app_entry.rep_id
        data_item["archived"] = app_entry.archived
        data_item["save_me"] = app_entry.save_me

        docs_to_put = []

        item = data_item
        fnames = item["first_name"].lower()
        fname_str = ""
        for fname in fnames.split(" "):
            fnayme = ""
            if len(fname) > 0:
                fnayme = str(fname[0]).upper() + fname[1:]
            else:
                fnayme = fname.upper()

            fname_str += (fnayme + " ")

        fname_str = fname_str[0:-1]

        lnames = item["last_name"].lower()
        lname_str = ""
        for lname in lnames.split(" "):
            lnayme = ""
            if len(lname) > 0:
                lnayme = str(lname[0]).upper() + lname[1:]
            else:
                lnayme = lname.upper()

            lname_str += (lnayme + " ")

        lname_str = lname_str[0:-1]

        name_title_cased = fname_str + " " + lname_str
        spouse_name_title_cased = "n/a"
        if not app_entry.spouse_name == "n/a":
            fnames2 = item["spouse_name"].lower()
            fname_str2 = ""
            for fname2 in fnames2.split(" "):
                fnayme2 = ""
                if len(fname2) > 0:
                    fnayme2 = str(fname2[0]).upper() + fname2[1:]
                else:
                    fnayme2 = fname2.upper()

                fname_str2 += (fnayme2 + " ")

            fname_str2 = fname_str2[0:-1]

            lnames2 = item["last_name"].lower()
            lname_str2 = ""
            for lname2 in lnames2.split(" "):
                lnayme2 = ""
                if len(lname2) > 0:
                    lnayme2 = str(lname2[0]).upper() + lname2[1:]
                else:
                    lnayme2 = lname2.upper()

                lname_str2 += (lnayme2 + " ")

            lname_str2 = lname_str2[0:-1]

            spouse_name_title_cased = fname_str2 + " " + lname_str2

        docs_to_put.append(
            search.Document(
                fields=[
                    search.TextField(name="cust_identifier", value=item["identifier"]),
                    search.TextField(name="cust_name", value=item["first_name"] + " " + item["last_name"]),
                    search.TextField(name="cust_name_l", value=item["first_name"].lower() + " " + item["last_name"].lower()),
                    search.TextField(name="cust_name_title_case", value=name_title_cased),
                    search.TextField(name="rep_id", value=item["rep_id"]),
                    search.TextField(name="spouse", value=spouse_name_title_cased)
                ]
            )
        )

        index = search.Index(name="cust_names")
        index.put(docs_to_put)

        index2 = search.Index(name="cust_addies2")
        docs_to_put2 = []
        docs_to_put2.append(
            search.Document(
                fields=[
                    search.TextField(name="identifier", value=app_entry.identifier),
                    search.TextField(name="cust_address", value=app_entry.customer_address),
                    search.TextField(name="cust_city_state", value=app_entry.customer_city + ", " + app_entry.customer_state),
                    search.TextField(name="cust_postal", value=app_entry.customer_postal),
                    search.TextField(name="cust_address_full", value=app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal)
                ]
            )
        )
        index2.put(docs_to_put2)


        if app_entry.usage_info_available:
            app_entry.usage_months = int(self.request.get("usage_months"))
            app_entry.total_kwhs = float(self.request.get("total_kwhs"))
            app_entry.total_dollars = float(self.request.get("total_dollars"))
            app_entry.highest_amount = float(self.request.get("highest_bill"))
            app_entry.usage_data = self.request.get("usage_data")

        #score = Helpers.check_credit(app_entry)
        #if not score is None:
        #    booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
        #    if not booking is None:
        #        sources = Helpers.list_funds()
        #        sources.pop(0)
        #        sources.pop(len(sources) - 1)

        #        brake = False
        #        for source in sources:
        #            if brake:
        #                continue

        #            if "active" in source.keys():
        #                if source["active"] == True:
        #                    if (score >= source["credit_floor_great"] and score <= source["credit_ceiling_great"]) or (score >= source["credit_floor_good"] and score <= source["credit_ceiling_good"]):
        #                        booking.fund = source["value"]
        #                        booking.put()
        #                        usr = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
        #                        CustomerTranscriber.transcribe(app_entry, usr, "fund_set")
        #                        brake = True
        #time.sleep(3)
        #c_check = CreditCheck.first(CreditCheck.field_app_identifier == app_entry.identifier)
        #if not c_check is None:0
        #        try:
        #            c_check.last_four = int(self.request.get("last_four"))
        #        except:
        #            c_check.last_four = -1
        #        c_check.put()

        c_check = CreditCheck(
            identifier=Helpers.guid(),
            field_app_identifier=app_entry.identifier,
            success=False,
            score=-1,
            last_four=1111,
            recorded_dt=Helpers.pacific_now()
        )
        c_check.put()

        if str(self.request.get("has_second_person")) == "1":
            app_entry.spouse_name = self.request.get("second_person_first").strip().title() + " " + self.request.get("second_person_last").strip().title()

        
        app_entry.put()
        if create_lead:
            lead = Lead(
                identifier=Helpers.guid(),
                field_app_identifier=app_entry.identifier,
                rep_identifier=self.request.get("user_identifier"),
                solar_pro_identifier="-1",
                status="default",
                dt_accepted=Helpers.pacific_now(),
                dt_created=Helpers.pacific_now(),
                archived=False,
                save_me=False
            )
            lead.put()
        usr = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
        if not usr is None:
            special_sp2_offset = Helpers.get_sp2_special_offset(self.request.get("rep_office"))
            ev = CalendarEvent(
                identifier=Helpers.guid(),
                field_app_identifier=app_entry.identifier,
                name=app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + " - SP2",
                all_day=False,
                calendar_key=usr.identifier,
                event_key="sp2",
                repeated=False,
                repeated_days="[]",
                details="Appointment with "  + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + ".\n" + app_entry.customer_address + "\n" + app_entry.customer_city + ", " + app_entry.customer_state + "\n" + app_entry.customer_postal + "\n" + Helpers.format_phone_number(app_entry.customer_phone),
                color="yellow",
                exception_dates="[]",
                google_series_id="-1",
                owners=json.dumps(["-1"]),
                start_dt=new_sp2,
                end_dt=new_sp2 + timedelta(minutes=119 - special_sp2_offset)
            )
            ev.put()
        if not (str(self.request.get("meter_number")) == "n/a"):
            meter_kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="SDGE_meter_number_" + app_entry.identifier,
                val=str(self.request.get("meter_number")),
                expiration=datetime(1970, 1, 1)
            )
            meter_kv.put()

        source_kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="app_entry_source_" + app_entry.identifier,
            val=str(self.request.get("source")),
            expiration=datetime(1970,1, 1)
        )
        source_kv.put()

        second_homeowner_dict = {}
        if str(self.request.get("has_second_person")) == "1":
            s_email = str(self.request.get("second_person_email").strip())
            if len(s_email) == 0:
                s_email = "didnt_want_to_provide_email@no_domain.com"

            second_homeowner_dict = {"first_name": self.request.get("second_person_first"), "last_name": self.request.get("second_person_last"), "email": s_email, "last_four": self.request.get("second_person_last_four")}
            second_person_kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="second_homeowner_" + app_entry.identifier,
                val=json.dumps(second_homeowner_dict),
                expiration=datetime(1970, 1, 1)
            )
            second_person_kv.put()
        try:
            cust_folder_id = Helpers.create_customer_folder_in_google_drive(app_entry,
                                                                        Helpers.get_root_customer_folder(),
                                                                        app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                                                                        "root_folder")

            qual_card_folder_id = Helpers.create_customer_folder_in_google_drive(app_entry, cust_folder_id, "Qual Card", "qual_card")

            if str(self.request.get("has_qual_card")) == "1":
                Helpers.create_file_in_google_drive(qual_card_folder_id, "qualcard." + pic_ext, file_content_b64, pic_mime)

        except:
            logging.error("Couldn't post qual card to google drive")

        user = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)



        try:
            CustomerTranscriber.transcribe(app_entry, user, "sales_form_post")
        except:
            logging.error("Couldn't record customer note on sales form post.")

        try:
            CustomerTranscriber.transcribe(app_entry, user, "sp2_set")
        except:
            logging.error("Couldn't record SP2 appointment being set on sales form post.")
        #try:
            #CustomerTranscriber.transcribe(app_entry, user, "survey_booked")
        #except:
            #logging.error("Couldn't record survey booked note on sales form post.")

        if self.configuration["customer_progress_v2"]:
            CustomerProgressManager.progress("account_creation", "account_created", Helpers.pacific_today(), app_entry, booking)


        token = None
        if not is_utah:
            x = 25
            #Helpers.create_CPF_customer_from_field_app_entry(app_entry)
            #if int(app_entry.customer_cpf_id) > 1:
                #try:
                    #CustomerTranscriber.transcribe(app_entry, user, "crm_work_cpf")
                #except:
                    #logging.error("Couldn't record customer being recorded into CPF as a customer note entry")
        else:
            token = "-1"
            #token = Helpers.create_mosaic_customer_from_field_app_entry(app_entry)

        #template_vars = {}
        #template_vars["cust_name"] = app_entry.customer_first_name + " " + app_entry.customer_last_name
        #days_map = {"1": "Monday", "2": "Tuesday", "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}
        #months_map = {"1": "January", "2": "February", "3": "March", "4": "April", "5": "May", "6": "June", "7": "July", "8": "August", "9": "September", "10": "October", "11": "November", "12": "December"}
        #booking_dayyy = date(booking.booking_year, booking.booking_month, booking.booking_day)
        #template_vars["dayofweek"] = days_map[str(booking_dayyy.isoweekday())]
        #template_vars["month_name"] = months_map[str(booking.booking_month)]
        #template_vars["day"] = str(booking.booking_day)
        #template_vars["sp2_dayofweek"] = days_map[str(new_sp2.isoweekday())]
        #template_vars["sp2_month_name"] = months_map[str(new_sp2.month)]
        #template_vars["sp2_day"] = str(new_sp2.day)
        #template_vars["sp2_hour"] = str(new_sp2.hour)

        #template_vars["sp2_min"] = self.request.get("sp2_mins")
        #if len(template_vars["sp2_min"]) == 1:
        #    template_vars["sp2_min"] = "0" + template_vars["sp2_min"]

        #template_vars["sp2_ampm"] = self.request.get("sp2_ampm").upper()
        # get the rep's name from the FieldApplicationUser store
        #template_vars["rep_name"] = "New Power"
        #the_reps = FieldApplicationUser.query(FieldApplicationUser.rep_id == booking.associated_rep_id)
        #for the_rep in the_reps:
            #template_vars["rep_name"] = the_rep.first_name + " " + the_rep.last_name

        #template_vars["rep_name"] = str(self.session["user_name"])
        #template_vars["rep_phone"] = Helpers.format_phone_number(app_entry.rep_phone)

        #Helpers.send_html_email(app_entry.customer_email, "Confirmation from New Power", "field_form_cust_notify", template_vars)
        #if not is_utah:
            #Helpers.send_html_email(app_entry.rep_email, "Confirmation from New Power", "field_form_cust_notify_ca", template_vars)
        #else:
            #Helpers.send_html_email(app_entry.rep_email, "Confirmation from New Power", "field_form_cust_notify_ut", template_vars)

        #store a mapping of the customer email to the rep email in the key value database
        kv_key = base64.b64encode(app_entry.customer_first_name.lower() + "_" + app_entry.customer_last_name.lower() + "_cust_name_to_rep_email")
        kv_val = app_entry.rep_email

        kv_store_item = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy=kv_key,
            val=kv_val,
            expiration=datetime(1970, 1, 1)
        )
        kv_store_item.put()

        kv_key2 = "cust_email_for_" + app_entry.customer_first_name + "_" + app_entry.customer_last_name
        kv_val2 = app_entry.customer_email

        kv_store_item2 = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy=kv_key2,
            val=kv_val2,
            expiration=datetime(1970, 1, 1)
        )
        kv_store_item2.put()

        #mortgage_income_allowed_chars = [".", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        #mortgage_str = ""
        #income_str = ""
        #mortgage_from_post = str(self.request.get("monthly_mortgage"))
        #income_from_post = str(self.request.get("annual_income"))
        #for ch in mortgage_from_post:
        #    if ch in mortgage_income_allowed_chars:
        #        mortgage_str += ch
        #for ch in income_from_post:
        #    if ch in mortgage_income_allowed_chars:
        #        income_str += ch

        #if income_str == "":
        #    income_str = "-1"
        #if mortgage_str == "":
        #    mortgage_str = "-1"

        #kv_item3 = KeyValueStoreItem(
        #    identifier=Helpers.guid(),
        #    keyy="mortgage_payment_" + field_app_id,
        #    val=mortgage_str,
        #    expiration=datetime(1970, 1, 1)   
        #)
        #kv_item3.put()

        #kv_item4 = KeyValueStoreItem(
        #    identifier=Helpers.guid(),
        #    keyy="annual_income_" + field_app_id,
        #    val=income_str,
        #    expiration=datetime(1970, 1, 1)
        #)
        #kv_item4.put()

        kv_item5 = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="lead_status_" + field_app_id,
            val=self.request.get("lead_status"),
            expiration=datetime(1970, 1, 1)
        )
        kv_item5.put()


        lb_stat = LeaderBoardStat(
            identifier=Helpers.guid(),
            rep_id=app_entry.rep_id,
            dt=Helpers.pacific_now(),
            metric_key="leads_acquired",
            office_identifier=app_entry.office_identifier,
            field_app_identifier=app_entry.identifier,
            in_bounds=True,
            pin_identifier="-1"
        )
        if True or self.request.get("lead_status") == "0":
            lb_stat.put()

        full_ab = LeaderBoardStat(
            identifier=Helpers.guid(),
            rep_id=app_entry.rep_id,
            dt=Helpers.pacific_now(),
            metric_key="full_ab",
            office_identifier=app_entry.office_identifier,
            field_app_identifier=app_entry.identifier,
            in_bounds=True,
            pin_identifier="-1"
        )

        if str(self.request.get("ab_partial")) == "0":
            full_ab.put()

        partial_ab = LeaderBoardStat(
            identifier=Helpers.guid(),
            rep_id=app_entry.rep_id,
            dt=Helpers.pacific_now(),
            metric_key="partial_ab",
            office_identifier=app_entry.office_identifier,
            field_app_identifier=app_entry.identifier,
            in_bounds=True,
            pin_identifier="-1"
        )

        if str(self.request.get("ab_partial")) == "1":
            partial_ab.put()

        #if app_identity.get_application_id() in ["npfieldapp"] and (not booking.fund == "cash"):
        #    from google.appengine.api import taskqueue
        #    parameters = {"identifier": app_entry.identifier, "annual_income": income_str, "monthly_mortgage": mortgage_str, "last_four": self.request.get("last_four")}
        #    taskqueue.add(url="/tq/create_customer_in_dividend", params=parameters)
        #    if str(self.request.get("has_second_person")) == "1":
        #        parameters2 = json.loads(json.dumps(parameters))                
        #        parameters2["second_homeowner"] = "1"
        #        parameters2["second_homeowner_dict"] = json.dumps(second_homeowner_dict)    
            #Helpers.create_customer_in_dividend(app_entry, income_str, mortgage_str)
        #        taskqueue.add(url="/tq/create_customer_in_dividend", params=parameters2)

        try:
            notification = Notification.first(Notification.action_name == "Sales Form Submitted")
            if not notification is None:
                msg = "new lead..." + user.first_name.lower().strip() + " " + user.last_name.lower().strip() + " [" + Helpers.format_phone_number(user.rep_phone) + "] picked up " + app_entry.customer_first_name.lower().strip() + " " + app_entry.customer_last_name.lower().strip() + "."
                for p in notification.notification_list:
                    Helpers.send_email(p.email_address, "New Lead", msg)
        except:
            y = 55

        if str(self.request.get("care_value")) == "1":
            note = CustomerNote(
                identifier=Helpers.guid(),
                field_app_identifier=app_entry.identifier,
                inserted_pacific=Helpers.pacific_now(),
                inserted_utc=datetime.now(),
                author=self.request.get("user_identifier"),
                perms="public",
                content=json.dumps({"txt": ["This customer is on a government-based discount program"]}),
                blob_count=0,
                note_key="welfare",
                read=True
            )
            note.put()

            override_kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="ab_override_" + app_entry.identifier,
                val="1",
                expiration=datetime(1970, 1, 1)

            )
            override_kv.put()

        f2 = GCSLockedFile("/ApplicationSettings/soiling_levels.json")
        soiling_data = json.loads(f2.read())
        f2.unlock()

        existing_postals = []

        for soiling_key in soiling_data.keys():
            for postal_code in soiling_data[soiling_key]:
                existing_postals.append(postal_code)

        if not app_entry.customer_postal in existing_postals:
            if app_identity.get_application_id() == "npfieldapp":
                Helpers.send_email("thomas@newpower.net", "New Zip Code in Sales Form", app_entry.customer_postal)

        logging_data_json = {}
        has_logger_data = str(self.request.get("data_logger_question")) == "1"
        logging_data_json["logging"] = has_logger_data
        if has_logger_data:
            logging_data_json["id"] = self.request.get("data_logger_id")
            logging_data_json["started"] = (self.request.get("started_logging") == "1")
            logging_data_json["location"] = self.request.get("data_logger_location")

        logging_kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy=app_entry.identifier + "_data_logging",
            val=json.dumps(logging_data_json),
            expiration=Helpers.pacific_now() + timedelta(days=180)
        )
        logging_kv.put()

        if has_logger_data:
            reader = SolarReader.first(SolarReader.hash == self.request.get("data_logger_id").strip().upper())
            if not reader is None:
                reader.field_app_identifier = app_entry.identifier
                reader.rep_ownership = self.request.get("user_identifier")
                reader.deployment_dt = Helpers.pacific_now()
                reader.checked_out = True
                reader.retrieval_dt = datetime(1970, 1, 1)
                reader.put()

                reader_stat = LeaderBoardStat(
                    identifier=Helpers.guid(),
                    rep_id=app_entry.rep_id,
                    dt=Helpers.pacific_now(),
                    metric_key="data_logger_deployed",
                    office_identifier=app_entry.office_identifier,
                    field_app_identifier=app_entry.identifier,
                    in_bounds=True,
                    pin_identifier="-1"
                )
                reader_stat.put()

        is_spanish = (str(self.request.get("spanish")) == "1")
        if is_spanish:
            spanish_kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy=app_entry.identifier + "_espanol",
                val="1",
                expiration=datetime(1970, 1, 1)
            )
            spanish_kv.put()

        sp2_str = ""
        if str(self.request.get("appointment_type")) in ["same_day_right_now", "same_day_later_on"]:
            subject = "Same Day AB - Get it While it's Hot"
            if str(self.request.get("appointment_type")) == "same_day_right_now":
                sp2_str = "SP2 Time: RIGHT NOW"
            else:
                am_pm = "AM"
                hour = app_entry.sp_two_time.hour
                if hour >= 12:
                    am_pm = "PM"
                if hour > 12:
                    hour -= 12
                sp2_str = "SP2 Time: " + str(hour) + ":00 " + am_pm
            msg = "SAME DAY AB! " + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + "): " + sp2_str
            msg += ". Address: " + app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal
            msg += ". KWHS: " + str(app_entry.total_kwhs)            

            sp = FieldApplicationUser.first(FieldApplicationUser.identifier == generator)
            if not sp is None:
                closer = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("closer"))
                if not closer is None:
                    msg += "\n\nSet By: " + sp.first_name.strip().title() + " " + sp.last_name.strip().title()
                    msg += "\nCloser: " + closer.first_name.strip().title() + " " + closer.last_name.strip().title()


            notification2 = Notification.first(Notification.action_name == "Same Day ABs")
            if not notification2 is None: 
                for person in notification2.notification_list:
                    Helpers.send_email(person.email_address, subject, msg)

        keyy = "allow_CPF_work_for_" + app_entry.identifier
        memcache.set(key=keyy, value="true", time=1800)

        redirect_url = "/success2?e_identifier=" + app_entry.identifier + "&b_identifier=" + booking.identifier
        if (self.request.get("has_qual_card") == "0"):
            redirect_url = "/sign/" + app_entry.identifier + "?bundle_key=sales_form"

        if len(str(self.request.get("closer"))) == 128:
            from google.appengine.api import taskqueue
            continuation_data = {}
            continuation_data["closer"] = str(self.request.get("closer"))
            continuation_data["app_entry_identifier"] = app_entry.identifier
            continuation_data["appointment_type"] = self.request.get("appointment_type")
            taskqueue.add(url="/tq/sales_form_closer_assignment", params=continuation_data, countdown=30)

            if self.request.get("user_identifier") in ["12f019d829c565a4fb4fc97bfa3c246889a709387bb5faa898ba776a8ea5e3e2ec05038fca8b3e662062c3c5dd15dae30ee8221a6881ea24d48cbbc4279b0dd3", "fff4eb8e26f78c8fc8ec1ca092dc94061f9b470e058cf91a3e0db3d902accb45c17b8744669a6ab2ce20e6bd9d0ea591ef2b6fbcf64c19bb0d02c86fba8da828"]:
                self.redirect("/appt_confirmation/"+ app_entry.identifier + "/" + self.request.get("closer"))
                return
            else:                
                self.redirect("/")
        else:
            self.redirect("/")




    else:
        self.response.out.write("The appointment slot was already taken. <br />Please resubmit the form with a new appointment date and be sure to change the lead ID recorded on paper")

