def mail_signed_docs(self):
    import time
    from datetime import datetime
    from datetime import timedelta
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    from google.appengine.api import taskqueue

    if 5 == 5:
        time.sleep(30)
        from PyPDF2 import PdfFileWriter,PdfFileReader
        from io import BytesIO
        import StringIO
        retryParameters = gcs.RetryParams(initial_delay=0.2,
                                                max_delay=5.0,
                                                backoff_factor=2,
                                                max_retry_period=15,
                                                urlfetch_timeout=30)

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name

        pdfs = []
        pdf_bytes = []
        cnt = 0
        cnt44 = "cnt44"
        split_filenames = []
        app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("identifier"))
        pending_user_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "new_user_registration_" + self.request.get("identifier"))
        if not app_entry is None:
            booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
            if not booking is None:
                proposal = CustomerProposalInfo.first(CustomerProposalInfo.field_app_identifier == app_entry.identifier)
                if proposal is None:
                    proposal = CustomerProposalInfo(
                        identifier=Helpers.guid(),
                        field_app_identifier=self.request.get("identifier"),
                        version=1
                    )
                    inf_dict = {}
                    inf_dict["system_size"] = "0"
                    inf_dict["panel_type"] = ""
                    inf_dict["panel_qty"] = "0"
                    inf_dict["new_panel_qty"] = "0"
                    inf_dict["inverter_type"] = ""
                    inf_dict["racking"] = ""
                    proposal.info = json.dumps(inf_dict)


                bundle_key = "rep_sales_docs"
                if len(str(self.request.get("bundle_key"))):
                    bundle_key = self.request.get("bundle_key")
                docs = ComposedDocument.query(ComposedDocument.bundle_key == bundle_key)                    
                doc_items = []
                for doc in docs:
                    doc_items.append(doc)

                

                doc_items = Helpers.bubble_sort(doc_items, "idx")

                app_entry_ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
                market_ol = None
                if not app_entry_ol is None:
                    market_ol = OfficeLocation.first(OfficeLocation.identifier == app_entry_ol.parent_identifier)


                supplement_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "secondary_fund_" + app_entry.identifier)
                if not supplement_kv is None:
                    setattr(booking, "secondary_fund", supplement_kv.val)

                roof_work_item = RoofWorkItem.first(RoofWorkItem.field_app_identifier == app_entry.identifier)
                if not roof_work_item is None:
                    roof_info = json.loads(roof_work_item.info)                        
                    setattr(app_entry, "reroof_type", roof_info["rep_selection_one"])
                    setattr(app_entry, "reroof_doc_type", roof_info["roof_type"])

                doc_tokens = []
                for doc in doc_items:
                    fn = Helpers.compile_document_formula(json.loads(doc.criteria)["formula"])
                    if fn["fn"](app_entry, booking, proposal, market_ol):
                        doc_tokens.append(doc.token)

                other_docs = ComposedDocument.query(ComposedDocument.name.IN(["Blank", "Customer Service Plan"]))   
                svc_file = GCSLockedFile("/CustomerService/bulk.json")
                svc_contents = svc_file.read()
                svc_file.unlock()
                if svc_contents is None:
                    svc_contents = "[]"

                deserialized_svc = json.loads(svc_contents)
                is_subscribed = False
                subscribed_price = 0
                for item in deserialized_svc:
                    if item["field_app_identifier"] == app_entry.identifier:
                        is_subscribed = True
                        subscribed_price = int(item["price"])
                
                for doc in other_docs:
                    if is_subscribed:
                        if subscribed_price > 0:
                            doc_tokens.append(doc.token)


                if app_entry.utility_provider == "southern_california_edison":
                    proposal.fix_additional_amount()
                    proposal.fix_system_size()
                    info3 = json.loads(proposal.info)
                    if float(info3["system_size"]) < 10.0:
                        edison_doc = ComposedDocument.first(ComposedDocument.name == "SCE Under 10KW")
                        if not edison_doc is None:
                            doc_tokens.append(edison_doc.token)
                    else:
                        edison_doc = ComposedDocument.first(ComposedDocument.name == "SCE Over 10KW")
                        if not edison_doc is None:
                            doc_tokens.append(edison_doc.token)

                cnt2 = 0
                for doc_token in doc_tokens:
                    #Helpers.send_email("rnirnber@gmail.com", "here", "kk")
                    filename_a = bucket + '/TempDocs/' + self.request.get("token") + "_" + doc_token + ".pdf"
                    file_a = gcs.open(filename_a, 'r', retry_params=retryParameters)
                    pdf_bytes.append(BytesIO(file_a.read()))
                    pdfs.append(PdfFileReader(pdf_bytes[cnt]))
                    file_a.close()
                    #gcs.delete(filename_a)
                    cnt += 1
                    split_filenames.append('/TempDocs/' + self.request.get("token") + "_" + doc_token + ".pdf")

                #Helpers.send_email("rnirnber@gmail.com", "here2", "kk2")
                out_pdf = PdfFileWriter()
                for pdf in pdfs:
                    pdf_page_cnt = 0
                    while pdf_page_cnt < pdf.getNumPages():
                        out_pdf.addPage(pdf.getPage(pdf_page_cnt))
                        pdf_page_cnt += 1

                filename_b = bucket + "/SignedDocs/" + app_entry.identifier + ".pdf"
                if bundle_key == "roof_work":
                    filename_b = bucket + "/RoofWorkDocs/" + app_entry.identifier + ".pdf"
                    items = [
                        FieldApplicationEntry.first(FieldApplicationEntry.identifier == app_entry.identifier),
                        SurveyBooking.first(SurveyBooking.field_app_identifier == app_entry.identifier),
                        CustomerProgressItem.first(CustomerProgressItem.field_app_identifier == app_entry.identifier),
                        PerfectPacketEntry.first(PerfectPacketEntry.field_application_identifier == app_entry.identifier),
                        PerfectPacketSubmission.first(PerfectPacketSubmission.field_application_identifier == app_entry.identifier),
                        PerfectPacketApproval.first(PerfectPacketApproval.field_application_identifier == app_entry.identifier),
                        Lead.first(Lead.field_app_identifier == app_entry.identifier)
                    ]

                    items_to_put = []
                    for item in items:
                        if not item is None:
                            item.save_me = False
                            item.archived = False
                            if hasattr(item, "save_me_reason"):
                                item.save_me_reason = "n/a"
                            items_to_put.append(item)                

                    if len(items_to_put) == 1:
                        items_to_put[0].put()
                    else:
                        ndb.put_multi(items_to_put)                

                if bundle_key == "sales_form":
                    filename_b = filename_b.replace("/SignedDocs", "/PreSignedDocs")
                    items = [
                        FieldApplicationEntry.first(FieldApplicationEntry.identifier == app_entry.identifier),
                        SurveyBooking.first(SurveyBooking.field_app_identifier == app_entry.identifier),
                        CustomerProgressItem.first(CustomerProgressItem.field_app_identifier == app_entry.identifier),
                        PerfectPacketEntry.first(PerfectPacketEntry.field_application_identifier == app_entry.identifier),
                        PerfectPacketSubmission.first(PerfectPacketSubmission.field_application_identifier == app_entry.identifier),
                        PerfectPacketApproval.first(PerfectPacketApproval.field_application_identifier == app_entry.identifier),
                        Lead.first(Lead.field_app_identifier == app_entry.identifier)
                    ]

                    items_to_put = []
                    for item in items:
                        if not item is None:
                            item.save_me = False
                            item.archived = False
                            if hasattr(item, "save_me_reason"):
                                item.save_me_reason = "n/a"
                            items_to_put.append(item)                

                    if len(items_to_put) == 1:
                        items_to_put[0].put()
                    else:
                        ndb.put_multi(items_to_put)
                
                    if app_entry.lead_generator == "-1":
                        now2 = Helpers.pacific_now() + timedelta(hours=1)
                        now3 = Helpers.pacific_now()
                        now4 = datetime(now2.year, now2.month, now2.day, now2.hour, 0, 0)
                        secs_diff = (now4 - now3).total_seconds()
                        minutes_diff = secs_diff / 60
                        if minutes_diff < 15:
                            now2 = now2 + timedelta(hours=1)

                        rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
                        if not rep is None:
                            jobs_file_name = "/CampaignJobs/" + str(now2.year) + "_" + str(now2.month) + "_" + str(now2.day) + "_" + str(now2.hour) + "_jobs.json"
                            job_f = GCSLockedFile(jobs_file_name)
                            jobs_content = job_f.read()
                            if jobs_content is None:
                                jobs_content = "[]"

                            jobs_data = json.loads(jobs_content)
                            jobs_data.append({"field_app_identifier": app_entry.identifier, "rep_identifier": rep.identifier, "key": "introductory_selfie_own"})
                            job_f.write(json.dumps(jobs_data), "application/json", "public-read")


                
                file_b = gcs.open(filename_b, 'w', content_type="application/pdf", options={'x-goog-meta-foo': 'foo',
                                                                                            'x-goog-meta-bar': 'bar',
                                                                                            'x-goog-acl': 'public-read'},
                                                                                    retry_params=write_retry_params)
                buff = StringIO.StringIO()
                out_pdf.write(buff)
                buff.seek(2)
                file_b.write(buff.getvalue())
                file_b.close()
                buff.seek(2)
                b64_string = base64.b64encode(buff.getvalue())

                cust_folder = ThirdPartyFolder.first(
                    ndb.AND
                    (
                        ThirdPartyFolder.folder_key == "root_folder",
                        ThirdPartyFolder.field_app_identifier == app_entry.identifier
                    )
                )
                if not cust_folder is None:
                    if bundle_key == "rep_sales_docs":                                                
                        signed_docs_folder = ThirdPartyFolder.first(
                            ndb.AND
                            (
                                ThirdPartyFolder.folder_key == "signed_docs",
                                ThirdPartyFolder.field_app_identifier == app_entry.identifier
                            )
                        )
                        signed_folder_id = ""
                        if signed_docs_folder is None:
                            if not Helpers.check_if_file_exists_in_google_drive("Signed Docs", cust_folder.foreign_id):
                                val = memcache.get("saving_docs_" + app_entry.identifier)
                                if val is None:
                                    memcache.set(key="saving_docs_" + app_entry.identifier, value="1", time=3600)
                                    signed_folder_id = Helpers.create_customer_folder_in_google_drive(app_entry, cust_folder.foreign_id, "Signed Docs", "signed_docs")
                                    Helpers.create_file_in_google_drive(signed_folder_id, "Doc.pdf", b64_string, "application/pdf")
                                    Helpers.create_file_in_google_drive(signed_folder_id, "link_to_latest_doc.txt", base64.b64encode("LINK:\r\n\r\nhttps://storage.googleapis.com/" + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name()) + "/SignedDocs/" + app_entry.identifier + ".pdf"), "text/plain")

                        else:
                            val = memcache.get("saving_docs_" + app_entry.identifier)
                            if val is None:
                                signed_folder_id = signed_docs_folder.foreign_id
                                Helpers.create_file_in_google_drive(signed_folder_id, "Doc.pdf", b64_string, "application/pdf")
                                Helpers.create_file_in_google_drive(signed_folder_id, "link_to_latest_doc.txt", base64.b64encode("LINK:\r\n\r\nhttps://storage.googleapis.com/" + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name()) + "/SignedDocs/" + app_entry.identifier + ".pdf"), "text/plain")
                                memcache.set(key="saving_docs_" + app_entry.identifier, value="1", time=3600)

                        buff.close()

                        d_counter = 1
                        for item in split_filenames:
                            f99 = GCSLockedFile(item)
                            content = f99.read()
                            b64_content = base64.b64encode(content)
                            Helpers.create_file_in_google_drive(signed_folder_id, "doc_" + str(d_counter) + ".pdf", b64_content, "application/pdf")
                            f99.unlock()

                            d_counter = d_counter + 1

                        for bytez in pdf_bytes:
                            bytez.close()

                        rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
                        if not rep is None:
                            mailed = not (memcache.get("mailed_docs_" + app_entry.identifier) is None)
                            if not mailed:
                                memcache.set(key="mailed_docs_" + app_entry.identifier, value="1", time=60 * 60)
                                msg = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + ",\n\nBelow is a link to your signed documents:\r\n\r\nhttps://storage.googleapis.com/" + app_identity.get_default_gcs_bucket_name() + "/SignedDocs/" + app_entry.identifier + ".pdf \r\n\r\n If you have any questions, please feel free to reach out to your rep (" + rep.first_name.strip().title() + " " + rep.last_name.strip().title() + ") via email or telephone.\n\n"
                                msg += Helpers.format_phone_number(rep.rep_phone) + "\n" + rep.rep_email
                                Helpers.send_email(app_entry.customer_email, "Your Signed Documents", msg)

                    elif bundle_key == "roof_work":
                        signed_docs_folder = ThirdPartyFolder.first(
                            ndb.AND
                            (
                                ThirdPartyFolder.folder_key == "roof_work",
                                ThirdPartyFolder.field_app_identifier == app_entry.identifier
                            )
                        )
                        signed_folder_id = ""
                        if signed_docs_folder is None:
                            if not Helpers.check_if_file_exists_in_google_drive("Roof Work", cust_folder.foreign_id):
                                val = memcache.get("saving_roof_docs_" + app_entry.identifier)
                                if val is None:
                                    memcache.set(key="saving_roof_docs_" + app_entry.identifier, value="1", time=3600)
                                    signed_folder_id = Helpers.create_customer_folder_in_google_drive(app_entry, cust_folder.foreign_id, "Roof Work", "roof_work")
                                    Helpers.create_file_in_google_drive(signed_folder_id, "RoofDoc.pdf", b64_string, "application/pdf")

                        else:
                            val = memcache.get("saving_roof_docs_" + app_entry.identifier)
                            if val is None:
                                signed_folder_id = signed_docs_folder.foreign_id
                                Helpers.create_file_in_google_drive(signed_folder_id, "RoofDoc.pdf", b64_string, "application/pdf")
                                memcache.set(key="saving_docs_" + app_entry.identifier, value="1", time=3600)

                        buff.close()

                        for bytez in pdf_bytes:
                            bytez.close()

                        rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
                        if not rep is None:
                            mailed = not (memcache.get("mailed_roof_docs_" + app_entry.identifier) is None)
                            if not mailed:
                                memcache.set(key="mailed_roof_docs_" + app_entry.identifier, value="1", time=60 * 60)
                                msg = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + ",\n\nBelow is a link to your signed documents:\r\n\r\nhttps://storage.googleapis.com/" + app_identity.get_default_gcs_bucket_name() + "/RoofWorkDocs/" + app_entry.identifier + ".pdf \r\n\r\n If you have any questions, please feel free to reach out to your rep (" + rep.first_name.strip().title() + " " + rep.last_name.strip().title() + ") via email or telephone.\n\n"
                                msg += Helpers.format_phone_number(rep.rep_phone) + "\n" + rep.rep_email
                                Helpers.send_email(app_entry.customer_email, "Your Signed Documents", msg)

                                primary_fund = "error"
                                secondary_fund = "No secondary fund"
                                booking = SurveyBooking.first(SurveyBooking.field_app_identifier == app_entry.identifier)
                                if not booking is None:
                                    funds = Helpers.list_funds()
                                    for f in funds:
                                        if f["value"] == booking.fund:
                                            primary_fund = f["value_friendly"]

                                    supplement_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "secondary_fund_" + app_entry.identifier)
                                    if not supplement_kv is None:
                                        funds = Helpers.list_funds()
                                        for f in funds:
                                            if f["value"] == supplement_kv.val:
                                                secondary_fund = f["value_friendly"]

                                extra_msg = "\n\n\nPrimary Fund: " + primary_fund + "\n\n\n" + "Secondary Fund: " + secondary_fund

                                notification = Notification.first(Notification.action_name == "Roof Docs Signed")
                                if not notification is None:
                                    for p in notification.notification_list:
                                        Helpers.send_email(p.email_address,"Roof Docs Signed", "Update:\r\n\r\n" + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + "has signed roof work docs." + extra_msg)

                                pp_sub = PerfectPacketSubmission.first(PerfectPacketSubmission.field_application_identifier == app_entry.identifier)
                                if not pp_sub is None:
                                    info2 = json.loads(pp_sub.extra_info)
                                    if "project_manager" in info2.keys():
                                        pm = FieldApplicationUser.first(FieldApplicationUser.identifier == info2["project_manager"])
                                        if not pm is None:
                                            Helpers.send_email(pm.rep_email, "Roof Docs Signed - " + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),  app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + " has signed roof work docs" + extra_msg)

                    elif bundle_key == "sales_form":
                        pre_signed_docs_folder = ThirdPartyFolder.first(
                            ndb.AND
                            (
                                ThirdPartyFolder.folder_key == "pre_signing_docs",
                                ThirdPartyFolder.field_app_identifier == app_entry.identifier
                            )
                        )
                        pre_signed_folder_id = ""
                        if pre_signed_docs_folder is None:
                            if not Helpers.check_if_file_exists_in_google_drive("Pre-Signed Docs", cust_folder.foreign_id):
                                val = memcache.get("saving_pre_docs_" + app_entry.identifier)
                                if val is None:
                                    memcache.set(key="saving_pre_docs_" + app_entry.identifier, value="1", time=3600)
                                    pre_signed_folder_id = Helpers.create_customer_folder_in_google_drive(app_entry, cust_folder.foreign_id, "Pre-Signed Docs", "pre_signing_docs")
                                    Helpers.create_file_in_google_drive(pre_signed_folder_id, "Doc.pdf", b64_string, "application/pdf")
                        else:
                            val = memcache.get("saving_pre_docs_" + app_entry.identifier)
                            if val is None:
                                pre_signed_folder_id = pre_signed_docs_folder.foreign_id
                                Helpers.create_file_in_google_drive(pre_signed_folder_id, "Doc.pdf", b64_string, "application/pdf")
                                memcache.set(key="saving_pre_docs_" + app_entry.identifier, value="1", time=3600)

                        buff.close()

                        for bytez in pdf_bytes:
                            bytez.close()

        elif (not pending_user_kv is None):
            pending_user = json.loads(pending_user_kv.val)
            registrations_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pending_registrations")
            if registrations_kv is None:
                registrations_kv = KeyValueStoreItem(
                    identifier=Helpers.guid(),
                    keyy="pending_registrations",
                    val="[]",
                    expiration=datetime(1970, 1, 1)
                )
            pending_users = json.loads(registrations_kv.val)
            if not pending_user["identifier"] in pending_users:
                pending_users.append(pending_user["identifier"])
            registrations_kv.val = json.dumps(pending_users)
            registrations_kv.put()

            existing_stat = LeaderBoardStat.first(
                ndb.AND(
                    LeaderBoardStat.metric_key == "registrations",
                    LeaderBoardStat.field_app_identifier == pending_user["identifier"]
                )
            )
            if existing_stat is None:
                stat = LeaderBoardStat(
                    identifier=Helpers.guid(),
                    rep_id=pending_user["user_rep_id"],
                    dt=Helpers.pacific_now(),
                    metric_key="registrations",
                    office_identifier=pending_user["user_office"],
                    field_app_identifier=pending_user["identifier"],
                    in_bounds=True,
                    pin_identifier="-1"
                )
                stat.put()
                        
            bundle_key = "rep_employment_docs"
            if len(str(self.request.get("bundle_key"))) > 4:
                bundle_key = self.request.get("bundle_key")
            docs = ComposedDocument.query(ComposedDocument.bundle_key == bundle_key)
            doc_items = []
            for doc in docs:
                doc_items.append(doc)

            doc_items = Helpers.bubble_sort(doc_items, "idx")

            doc_tokens = []

            for doc in doc_items:
                fn = Helpers.compile_document_formula(json.loads(doc.criteria)["formula"], True)
                if fn["fn"](pending_user):
                    doc_tokens.append(doc.token)

            for doc_token in doc_tokens:
                #Helpers.send_email("rnirnber@gmail.com", "here", "kk")
                filename_a = bucket + '/TempDocs/' + self.request.get("token") + "_" + doc_token + ".pdf"
                file_a = gcs.open(filename_a, 'r', retry_params=retryParameters)
                pdf_bytes.append(BytesIO(file_a.read()))
                pdfs.append(PdfFileReader(pdf_bytes[cnt]))
                file_a.close()
                #gcs.delete(filename_a)
                cnt += 1

            #Helpers.send_email("rnirnber@gmail.com", "here2", "kk2")
            out_pdf = PdfFileWriter()
            for pdf in pdfs:
                pdf_page_cnt = 0
                while pdf_page_cnt < pdf.getNumPages():
                    out_pdf.addPage(pdf.getPage(pdf_page_cnt))
                    pdf_page_cnt += 1

            filename_b = bucket + "/SignedDocs/" + pending_user["identifier"] + ".pdf"
            file_b = gcs.open(filename_b, 'w', content_type="application/pdf", options={'x-goog-meta-foo': 'foo',
                                                                                        'x-goog-meta-bar': 'bar',
                                                                                        'x-goog-acl': 'public-read',
                                                                                        'cache-control': 'no-cache'},
                                                                                retry_params=write_retry_params)
            buff = StringIO.StringIO()
            out_pdf.write(buff)
            buff.seek(2)
            file_b.write(buff.getvalue())
            file_b.close()
            buff.seek(2)
            b64_string = base64.b64encode(buff.getvalue())

            buff.close()

            for bytez in pdf_bytes:
                bytez.close()


            name = pending_user["user_first"].strip().title() + " " + pending_user["user_last"].strip().title()
            template_vars = {}
            template_vars["name"] = name

            new_user = FieldApplicationUser(
                identifier=pending_user["identifier"],
                first_name=pending_user["user_first"].strip().title(),
                last_name=pending_user["user_last"].strip().title(),
                main_office=pending_user["user_office"],
                rep_id=pending_user["user_rep_id"].upper(),
                rep_email=pending_user["user_email"].strip().lower(),
                rep_phone=Helpers.numbers_from_str(pending_user["user_phone"]),
                user_type=pending_user["user_type"],
                password=Helpers.hash_pass(pending_user["user_password"]),
                payscale_key="n/a",
                sales_rabbit_id=-1,
                current_status=-1,
                recruiter_rep_id="SHAF1021",
                allowed_offices=json.dumps([]),
                automatic_override_enabled=True,
                automatic_override_amount=0,
                automatic_override_designee="SHAF0920",
                address=pending_user["user_address"],
                postal=pending_user["user_postal"],
                city=pending_user["user_city"],
                state=pending_user["user_state"],
                registration_date=Helpers.pacific_today(),
                allowed_functions="[]",
                is_manager=False,
                is_project_manager=False,
                accepts_leads=False
            )

            if new_user.recruiter_rep_id in ["SHAF0420", "SHAF1021", "SHAF0920"]:
                new_user.recruiter_rep_id = "AZ0230"
                new_user.automatic_override_designee = "AZ0230"
                new_user.automatic_override_amount = 0.0
                new_user.automatic_override_enabled=False

            if new_user.recruiter_rep_id in ["VAND0127", "COLL0910"]:
                new_user.automatic_override_amount = 0.0
                new_user.automatic_override_enabled=False

            existing_user = FieldApplicationUser.first(FieldApplicationUser.identifier == new_user.identifier)
            if existing_user is None:
                new_user.put()

            points_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "user_points_" + new_user.identifier)
            if points_kv is None:
                points_kv = KeyValueStoreItem(
                    identifier=Helpers.guid(),
                    keyy="user_points_" + new_user.identifier,
                    val="0",
                    expiration=datetime(1970, 1, 1)
                )
                points_kv.put()

            Helpers.send_html_email(new_user.rep_email, "Your Application to New Power", "user_signs_up", template_vars)

            attachment_data = {}
            attachment_data["data"] = ["https://storage.googleapis.com" + bucket + "/SignedDocs/" + new_user.identifier + ".pdf"]
            attachment_data["content_types"] = ["application/pdf"]
            attachment_data["filenames"] = ["W9_I9_Agreement_" + name.replace(" ", "_") + ".pdf"]

            w4_warning = ""

            notification_msg1 = "Dear Administrator,\n\nA new user (" +  name + ") has requested access to register with the in-house npfieldapp.appspot.com app." + w4_warning + "If you would like to approve " + name + ", please visit the following link (must be signed-in):\n\n"
            notification_msg1 += "https://" + self.request.environ["SERVER_NAME"] + "/approve_user/" + new_user.identifier
            notification_msg1 += "\n\nPAPERWORK PACKET:\n" + attachment_data["data"][0]

            notification_entries = Notification.query(
                ndb.OR
                (
                    Notification.action_name == "User Registers for App (Email)",
                    Notification.action_name == "User Registers for App (SMS)",
                )
            )

            form_office = "unknown office"
            offices = OfficeLocation.query(OfficeLocation.parent_identifier != "n/a")

            for office in offices:

                if office.identifier == new_user.main_office:
                    form_office = office.name

                    notification_list2 = []
                    notification_list1 = []

                    for notification_entry in notification_entries:
                        for item in notification_entry.notification_list:
                            if notification_entry.action_name == "User Registers for App (Email)":
                                #Helpers.send_email(item.email_address, "Approve Access for " + name, notification_msg1, attachment_data)
                                notification_list1.append(item)
                            elif notification_entry.action_name == "User Registers for App (SMS)":
                                #Helpers.send_email(item.email_address, "Found talent!", "Talent acquired: " + name.lower() + " from " + city.lower() + ", " + state.lower() + "..." + str(form_office.lower()) + " office")
                                notification_list2.append(item)
                            else:
                                logging.info("Unkown action name")

                    for person in notification_list2:
                        Helpers.send_email(person.email_address, "Found talent!", "Talent acquired: " + name.lower() + " from " + pending_user["user_city"].lower() + ", " + pending_user["user_state"].lower() + "..." + str(form_office.lower()) + " office")
                    for person in notification_list1:
                        Helpers.send_email(person.email_address, "Approve Access for " + name, notification_msg1)
                        #Helpers.send_email(person.email_address, "Approve Access for " + name, notification_msg1, attachment_data)

            #gcs.delete(bucket + "/SignedDocs/" + pending_user["identifier"] + ".pdf")
            if existing_user is None:
                new_user.put()
    else:
        yyy = 22
