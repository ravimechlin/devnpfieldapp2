def post(self):
    is_utah = ( (self.request.get("cust_state").upper() == "UT") or (self.request.get("cust_state").upper() == "UTAH") )
    self.session = get_current_session()
    tyme = int(time.time() * 1000)
    file_content = self.request.POST.multi['pic'].file.read()
    new_id = Helpers.guid()
    pic_name = self.request.params["pic"].filename.lower()
    name_elements = pic_name.split(".")
    pic_type = name_elements[len(name_elements) - 1]
    pic_ext = ""
    pic_mime = ""
    if pic_type == "png":
        pic_ext = "png"
        pic_mime = "image/png"
    else:
        pic_ext = "jpg"
        pic_mime = "image/jpg"

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
        slot_number=int(self.request.get("appt_slot_num")),
        booking_day=int(appt_date_items[1]),
        booking_month=int(appt_date_items[0]),
        booking_year=int(appt_date_items[2]),
        address=self.request.get("cust_address"),
        city=self.request.get("cust_city"),
        state=self.request.get("cust_state"),
        postal=self.request.get("cust_postal"),
        phone_number=self.request.get("cust_phone"),
        email=self.request.get("cust_email"),
        name=fixed_name,
        completion_state=0,
        associated_rep_id=self.request.get("rep_id").upper(),
        utility_no=self.request.get("cust_utility_account_no"),
        notes="",
        fund="n/a",
        trust_docs="n/a",
        utility_provider=self.request.get("cust_utility_provider"),
		archived=False,
        save_me=False
    )
    success = True
    bookings = SurveyBooking.query(
        ndb.AND(
            SurveyBooking.booking_day == int(appt_date_items[1]),
            SurveyBooking.booking_month == int(appt_date_items[0]),
            SurveyBooking.booking_year == int(appt_date_items[2]),
            SurveyBooking.slot_number == int(self.request.get("appt_slot_num")),
            SurveyBooking.office_identifier == self.request.get("rep_office"),
            ndb.OR(
                SurveyBooking.completion_state == 0,
                SurveyBooking.completion_state == 1,
                SurveyBooking.completion_state == 2,
                SurveyBooking.completion_state == 3
                )
        )
    )

    for booking_item in bookings:
        success = (not booking_item.archived)

    if success:
        booking.put()

        # clear the cache reservation
        full_key = self.request.get("rep_office") + "_" + appt_date_items[1] + "_" + appt_date_items[0] + "_" + appt_date_items[2] + "_" + "slot_" + self.request.get("appt_slot_num")
        key = hashlib.md5(full_key).hexdigest()
        memcache.delete(key)

        sig_date_items = self.request.get("cust_signature_date").split("-")
        sig_date = date(
            int(sig_date_items[2]),
            int(sig_date_items[0]),
            int(sig_date_items[1])
        )

        dob_date_items = self.request.get("cust_dob").split("-")
        dob_date = date(
            int(dob_date_items[2]),
            int(dob_date_items[0]),
            int(dob_date_items[1])
        )

        #build out a datetime value
        sp2_date_items = self.request.get("sp2_date").split("-")
        sp2_dt_start = datetime(int(sp2_date_items[2]), int(sp2_date_items[0]), int(sp2_date_items[1]))
        h = int(self.request.get("sp2_hours"))

        if h == 12 and self.request.get("sp2_ampm") == "AM":
            h = 0

        elif h < 12 and self.request.get("sp2_ampm") == "PM":
            h += 12

        sp2_dt_with_hours_added = sp2_dt_start + timedelta(hours=h)
        sp2_dt_with_mins_added = sp2_dt_with_hours_added + timedelta(minutes=int(self.request.get("sp2_mins")))

        app_entry = FieldApplicationEntry(
            identifier=field_app_id,
            office_identifier=self.request.get("rep_office"),
            booking_identifier=booking.identifier,
            customer_signature_date=sig_date,
            customer_first_name=self.request.get("cust_first")[0].upper() + self.request.get("cust_first")[1:],
            customer_last_name=self.request.get("cust_last")[0].upper() + self.request.get("cust_last")[1:],
            customer_email=self.request.get("cust_email"),
            customer_phone=self.request.get("cust_phone"),
            customer_dob=dob_date,
            customer_postal=self.request.get("cust_postal"),
            customer_city=self.request.get("cust_city"),
            customer_state=self.request.get("cust_state"),
            customer_address=self.request.get("cust_address"),
            customer_cpf_id=-1,
            customer_utility_account_number=self.request.get("cust_utility_account_no"),
            customer_kwh_price="-1.0",
            rep_id=self.request.get("rep_id"),
            rep_email=self.request.get("rep_email"),
            rep_phone=self.request.get("rep_phone"),
            rep_lead_id=self.request.get("lead_id_real"),
            insert_time=tyme,
            processed=False,
            image_extension=pic_ext,
            opt_rep_notes=self.request.get("notes_for_surveyor"),
            sp_two_time = sp2_dt_with_mins_added,
            utility_provider=self.request.get("cust_utility_provider"),
            customer_mosaic_id=-1,
			archived=False,
			archive_reason="n/a",
            has_holds=False,
            hold_items="[]",
            save_me=False,
            save_me_reason="n/a",
            save_me_dt=datetime(1970, 1, 1),
            hide_from_recent_view=False,
            usage_info_available=False,
            usage_months=0,
            total_kwhs=float(0),
            total_dollars=float(0),
            proposal_state=0,
            tier_option="A",
            deal_closed=False,
            new_survey_state=0,
            deal_locked=False
        )
        app_entry.put()
        user = None

        try:
            user = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
            CustomerTranscriber.transcribe(app_entry, user, "sales_form_post")
        except:
            logging.error("Couldn't record customer note on sales form post.")

        try:
            CustomerTranscriber.transcribe(app_entry, user, "sp2_set")
        except:
            logging.error("Couldn't record SP2 appointment being set on sales form post.")
        try:
            CustomerTranscriber.transcribe(app_entry, user, "survey_booked")
        except:
            logging.error("Couldn't record survey booked note on sales form post.")

        if self.configuration["customer_progress_v2"]:
            CustomerProgressManager.progress("account_creation", "account_created", Helpers.pacific_today(), app_entry, booking)

        token = None
        if not is_utah:
            #Helpers.create_CPF_customer_from_field_app_entry(app_entry)
            if int(app_entry.customer_cpf_id) > 1:
                try:
                    CustomerTranscriber.transcribe(app_entry, user, "crm_work_cpf")
                except:
                    logging.error("Couldn't record customer being recorded into CPF as a customer note entry")
        else:
            token = "-1"
            #token = Helpers.create_mosaic_customer_from_field_app_entry(app_entry)

        template_vars = {}
        template_vars["cust_name"] = app_entry.customer_first_name + " " + app_entry.customer_last_name
        days_map = {"1": "Monday", "2": "Tuesday", "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}
        months_map = {"1": "January", "2": "February", "3": "March", "4": "April", "5": "May", "6": "June", "7": "July", "8": "August", "9": "September", "10": "October", "11": "November", "12": "December"}
        booking_dayyy = date(booking.booking_year, booking.booking_month, booking.booking_day)
        template_vars["dayofweek"] = days_map[str(booking_dayyy.isoweekday())]
        template_vars["month_name"] = months_map[str(booking.booking_month)]
        template_vars["day"] = str(booking.booking_day)
        template_vars["sp2_dayofweek"] = days_map[str(sp2_dt_start.isoweekday())]
        template_vars["sp2_month_name"] = months_map[str(sp2_dt_start.month)]
        template_vars["sp2_day"] = str(sp2_dt_start.day)
        template_vars["sp2_hour"] = self.request.get("sp2_hours")
        if len(template_vars["sp2_hour"]) == 0:
            template_vars["sp2_hour"] = "0" + template_vars["sp2_hour"]

        template_vars["sp2_min"] = self.request.get("sp2_mins")
        if len(template_vars["sp2_min"]) == 1:
            template_vars["sp2_min"] = "0" + template_vars["sp2_min"]

        template_vars["sp2_ampm"] = self.request.get("sp2_ampm").upper()
        # get the rep's name from the FieldApplicationUser store
        template_vars["rep_name"] = "New Power"
        the_reps = FieldApplicationUser.query(FieldApplicationUser.rep_id == booking.associated_rep_id)
        for the_rep in the_reps:
            template_vars["rep_name"] = the_rep.first_name + " " + the_rep.last_name

        #template_vars["rep_name"] = str(self.session["user_name"])
        template_vars["rep_phone"] = Helpers.format_phone_number(app_entry.rep_phone)

        #Helpers.send_html_email(app_entry.customer_email, "Confirmation from New Power", "field_form_cust_notify", template_vars)
        if not is_utah:
            Helpers.send_html_email(app_entry.rep_email, "Confirmation from New Power", "field_form_cust_notify_ca", template_vars)
        else:
            Helpers.send_html_email(app_entry.rep_email, "Confirmation from New Power", "field_form_cust_notify_ut", template_vars)

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

        try:
            Helpers.increment_tally_for_user(booking.associated_rep_id, "surveys_booked")
        except:
            logging.info(".")

        try:
            notification = Notification.first(Notification.action_name == "Sales Form Submitted")
            if not notification is None:
                msg = "new lead..." + user.first_name.lower().strip() + " " + user.last_name.lower().strip() + " [" + Helpers.format_phone_number(user.rep_phone) + "] picked up " + app_entry.customer_first_name.lower().strip() + " " + app_entry.customer_last_name.lower().strip() + "."
                for p in notification.notification_list:
                    Helpers.send_email(p.email_address, "New Lead", msg)
        except:
            y = 55

        keyy = "allow_CPF_work_for_" + app_entry.identifier
        memcache.set(key=keyy, value="true", time=1800)
        if not is_utah:
            #uncomment line below to re-enable CPF
            #self.redirect("/success?e_identifier=" + app_entry.identifier + "&b_identifier=" + booking.identifier)
            self.redirect("/success2?e_identifier=" + app_entry.identifier + "&b_identifier=" + booking.identifier)
            #template_values = {}
            #template_values["location"] = "continue"
            #template_values["app_entry_identifier"] = app_entry.identifier
            #template_values["booking_identifier"] = booking.identifier

            #path = Helpers.get_html_path('client_side_redirect.html')
            #self.response.out.write(template.render(path, template_values))
        else:
            self.redirect("/poll_form_workers?e_identifier=" + app_entry.identifier + "&b_identifier=" + booking.identifier + "&tk_identifier=" + token)




    else:
        self.response.out.write("The appointment slot was already taken. <br />Please resubmit the form with a new appointment date and be sure to change the lead ID recorded on paper")

