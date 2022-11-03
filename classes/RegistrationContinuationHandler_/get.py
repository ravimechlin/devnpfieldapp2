def get(self, step_no, user_identifier):
    import StringIO
    import base64
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from PyPDF2 import PdfFileWriter,PdfFileReader

    step_no = int(step_no)
    retryParameters = gcs.RetryParams(initial_delay=0.2,
                                               max_delay=5.0,
                                               backoff_factor=2,
                                               max_retry_period=15,
                                               urlfetch_timeout=30)

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)


    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    usr_dict = memcache.get("temp_pending_user_registration_" + user_identifier)
    state = memcache.get("user_registration_state_for_" + user_identifier)
    city = memcache.get("user_registration_city_for_" + user_identifier)

    if usr_dict is None or state is None or city is None:
        logging.info("Could not proceed")
    else:
        info_dct = Helpers.get_documentation_images(usr_dict["user_type"], state, ["w9", "i9", "agreement_signature", "before_signature_images", "after_signature_images"])

        if step_no >= 1 and step_no <= info_dct["agreement_page_count"]:

            exclusion_list = ["w9", "i9"]
            if not step_no == info_dct["signature_page_index"]:
                exclusion_list.append("agreement_signature")

            if step_no < info_dct["signature_page_index"]:
                exclusion_list.append("after_signature_images")

            if step_no > info_dct["signature_page_index"]:
                exclusion_list.append("before_signature_images")


            dict_key = "agreement_signature"
            if step_no < info_dct["signature_page_index"]:
                dict_key = "before_signature_images"
            elif step_no > info_dct["signature_page_index"]:
                dict_key = "after_signature_images"
            take_index = (dict_key == "before_signature_images" or dict_key == "after_signature_images")

            img_files = Helpers.get_documentation_images(usr_dict["user_type"], state, exclusion_list, step_no)

            file_to_read = img_files[dict_key]
            if take_index:
                pg_idx = step_no - 1

                if dict_key == "after_signature_images":
                    pg_idx = -1 + (step_no - info_dct["signature_page_index"])

                file_to_read = img_files[dict_key][pg_idx]

            pdf_bytez = BytesIO(file_to_read.read())
            pdf_page_img = Image.open(pdf_bytez)

            for key in ["agreement_signature", "before_signature_images", "after_signature_images"]:
                if key in img_files.keys():
                    if key == "agreement_signature":
                        img_files[key].close()
                    else:
                        for f in img_files[key]:
                            f.close()

            if step_no == 1:
                w9_i9_font_1 = ImageFont.truetype("Times.ttf", 41)

                twoday = Helpers.pacific_today()
                today_str = str(twoday.month)

                if twoday.month < 10:
                    today_str = "0" + today_str

                today_str += "/"

                if twoday.day < 10:
                    today_str += "0"

                today_str += "/"
                today_str += str(twoday.year)

                today_image = Image.new("RGBA", (420, 60), (255, 255, 255, 0))
                draw = ImageDraw.Draw(today_image)
                draw.text((5, 0), today_str, (0, 0, 0), font=w9_i9_font_1)

                full_name_image = Image.new("RGBA", (2060,45), (255,255,255, 0))
                draw = ImageDraw.Draw(full_name_image)
                draw.text((5, 0), usr_dict["first_name"] + " " + usr_dict["last_name"], (0,0,0), font=w9_i9_font_1)

                pdf_page_img.paste(today_image, (700, 506), today_image)
                pdf_page_img.paste(full_name_image, (1060, 562), full_name_image)

            user_sig_stream = None
            if step_no == info_dct["signature_page_index"]:
                w9_i9_font_1 = ImageFont.truetype("Times.ttf", 41)

                recruiters = FieldApplicationUser.query(FieldApplicationUser.rep_id == usr_dict["recruiter_rep_id"])
                for recruiter in recruiters:
                    recruiter_name_image = Image.new("RGBA", (900,60), (255,255,255))
                    draw = ImageDraw.Draw(recruiter_name_image)
                    draw.text((5, 0), recruiter.first_name + " " + recruiter.last_name, (0,0,0), font=w9_i9_font_1)

                    pdf_page_img.paste(recruiter_name_image, (1605, 2206), recruiter_name_image)

                    full_name_image = Image.new("RGBA", (2060,45), (255,255,255, 0))
                    draw = ImageDraw.Draw(full_name_image)
                    draw.text((5, 0), usr_dict["first_name"] + " " + usr_dict["last_name"], (0,0,0), font=w9_i9_font_1)

                    pdf_page_img.paste(full_name_image, (1605, 2005), full_name_image)

                    sig_b64_file = gcs.open(bucket + "/TempDocs/" + usr_dict["identifier"] + "_sig.txt", 'r', retry_params=retryParameters)
                    user_sig_stream = BytesIO(base64.b64decode(sig_b64_file.read()))
                    user_sig_image = Image.open(user_sig_stream)
                    sig_b64_file.close()

                    pdf_page_img.paste(user_sig_image, (1500, 1775), user_sig_image)

            buff = StringIO.StringIO()
            pdf_page_img.save(buff, "PDF", resolution=100.0, quality=30.0)
            buff.seek(2)
            pdf_doc = PdfFileReader(buff, False)

            output_docs=PdfFileWriter()
            output_docs.addPage(pdf_doc.getPage(0))

            #for before_sig_pdf in before_sig_pdfs:
             #   output_docs.addPage(before_sig_pdf.getPage(0))

            #output_docs.addPage(agreement_sig_pdf.getPage(0))
            #agreement_sig_pdf.stream = None

            #for after_sig_pdf in after_sig_pdfs:
             #   output_docs.addPage(after_sig_pdf.getPage(0))
             #   after_sig_pdf.stream = None

            #buff.close()
            #buff = StringIO.StringIO()
            buff.seek(2)
            output_docs.write(buff)
            buff.seek(2)

            filename = bucket + '/TempDocs/' + usr_dict["identifier"] + "_" + str(step_no + 1) + ".pdf"
            gcs_file = gcs.open(
                        filename,
                        'w',
                        content_type="application/pdf",
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar',
                                 'x-goog-acl': 'public-read'},
                        retry_params=write_retry_params
            )
            gcs_file.write(buff.getvalue())
            gcs_file.close()
            buff.close()
            pdf_bytez.close()

            if not user_sig_stream is None:
                user_sig_stream.close()

            Helpers.redirect_on_client(self.response, "/continue_registration/" + str(step_no + 1) + "/" + usr_dict["identifier"], 2000)
            return

        elif step_no > info_dct["agreement_page_count"] and step_no <= (info_dct["agreement_page_count"] * 2):
            if step_no == (info_dct["agreement_page_count"] + 1):
                filename_a = bucket + '/TempDocs/' + usr_dict["identifier"] + "_1.pdf"
                file_a = gcs.open(filename_a, 'r', retry_params=retryParameters)
                pdf_a_bytes = BytesIO(file_a.read())
                pdf_a = PdfFileReader(pdf_a_bytes)
                file_a.close()

                filename_b = bucket + '/TempDocs/' + usr_dict["identifier"] + "_2.pdf"
                file_b = gcs.open(filename_b, 'r', retry_params=retryParameters)
                pdf_b_bytes = BytesIO(file_b.read())
                pdf_b = PdfFileReader(pdf_b_bytes)
                file_b.close()

                out_pdf = PdfFileWriter()
                out_pdf.addPage(pdf_a.getPage(0))
                out_pdf.addPage(pdf_a.getPage(1))
                out_pdf.addPage(pdf_a.getPage(2))

                out_pdf.addPage(pdf_b.getPage(0))

                buff = StringIO.StringIO()
                out_pdf.write(buff)
                buff.seek(2)

                filename = bucket + "/TempDocs/" + usr_dict["identifier"] + "_A.pdf"
                gcs_file = gcs.open(
                    filename,
                    'w',
                    content_type="application/pdf",
                    options={'x-goog-meta-foo': 'foo',
                             'x-goog-meta-bar': 'bar',
                             'x-goog-acl': 'public-read'},
                    retry_params=write_retry_params
                )
                gcs_file.write(buff.getvalue())
                gcs_file.close()

                buff.close()
                pdf_a_bytes.close()
                pdf_b_bytes.close()

            else:
                next_letter_suffix = chr(65 + (step_no - info_dct["agreement_page_count"]) - 1)
                last_letter_suffix = chr(65 + (step_no - info_dct["agreement_page_count"]) - 2)

                filename_a = bucket + '/TempDocs/' + usr_dict["identifier"] + "_" + last_letter_suffix + ".pdf"
                file_a = gcs.open(filename_a, 'r', retry_params=retryParameters)
                pdf_bytes_a = BytesIO(file_a.read())
                pdf_a = PdfFileReader(pdf_bytes_a)
                file_a.close()

                out_pdf = PdfFileWriter()
                pdf_page_cnt = 0
                while pdf_page_cnt < pdf_a.getNumPages():
                    out_pdf.addPage(pdf_a.getPage(pdf_page_cnt))
                    pdf_page_cnt += 1

                filename_b = bucket + "/TempDocs/" + usr_dict["identifier"] + "_" + str(step_no - info_dct["agreement_page_count"] + 1) + ".pdf"
                file_b = gcs.open(filename_b, 'r', retry_params=retryParameters)
                pdf_bytes_b = BytesIO(file_b.read())
                pdf_b = PdfFileReader(pdf_bytes_b)
                file_b.close()

                out_pdf.addPage(pdf_b.getPage(0))

                buff = StringIO.StringIO()
                out_pdf.write(buff)
                buff.seek(2)

                filename = bucket + "/TempDocs/" + usr_dict["identifier"] + "_" + next_letter_suffix + ".pdf"
                gcs_file = gcs.open(
                    filename,
                    'w',
                    content_type="application/pdf",
                    options={'x-goog-meta-foo': 'foo',
                             'x-goog-meta-bar': 'bar',
                             'x-goog-acl': 'public-read'},
                    retry_params=write_retry_params
                )
                gcs_file.write(buff.getvalue())
                gcs_file.close()

                pdf_bytes_a.close()
                pdf_bytes_b.close()
                buff.close()

            Helpers.redirect_on_client(self.response, "/continue_registration/" + str(step_no + 1) + "/" + usr_dict["identifier"], 5000)
            return

        elif step_no > (info_dct["agreement_page_count"] * 2):
            diff = step_no - (info_dct["agreement_page_count"] * 2)
            if diff == 1:
                cnt = 1
                while cnt <= info_dct["agreement_page_count"] + 1:
                    gcs.delete(bucket + "/TempDocs/" + usr_dict["identifier"] + "_" + str(cnt) + ".pdf")
                    cnt += 1

                cnt = 65
                while cnt < 65 + info_dct["agreement_page_count"] - 1:
                    gcs.delete(bucket + "/TempDocs/" + usr_dict["identifier"] + "_" + chr(cnt) + ".pdf")
                    cnt += 1

                gcs.delete(bucket + "/TempDocs/" + usr_dict["identifier"] + "_sig.txt")

                Helpers.redirect_on_client(self.response, "/continue_registration/" + str(step_no + 1) + "/" + usr_dict["identifier"], 5000)
                return

            elif diff == 2:

                name = usr_dict["first_name"] + " " + usr_dict["last_name"]
                template_vars = {}
                template_vars["name"] = name

                new_user = FieldApplicationUser(
                    identifier=usr_dict["identifier"],
                    first_name=usr_dict["first_name"],
                    last_name=usr_dict["last_name"],
                    main_office=usr_dict["main_office"],
                    rep_id=usr_dict["rep_id"],
                    rep_email=usr_dict["rep_email"],
                    rep_phone=usr_dict["rep_phone"],
                    user_type=usr_dict["user_type"],
                    password=usr_dict["password"],
                    payscale_key="n/a",
                    sales_rabbit_id=-1,
                    current_status=-1,
                    recruiter_rep_id=usr_dict["recruiter_rep_id"],
                    allowed_offices=usr_dict["allowed_offices"],
                    automatic_override_enabled=usr_dict["automatic_override_enabled"],
                    automatic_override_amount=usr_dict["automatic_override_amount"],
                    automatic_override_designee=usr_dict["automatic_override_designee"],
                    registration_date=Helpers.pacific_today(),
                    allowed_functions="[]",
                    is_manager=False,
                    is_project_manager=False,
                    accepts_leads=False
                )
                new_user.put()
                points_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "user_points_" + usr_dict["identifier"])
                if points_kv is None:
                    points_kv = KeyValueStoreItem(
                        identifier=Helpers.guid(),
                        keyy="user_points_" + usr_dict["identifier"],
                        val="0",
                        expiration=datetime(1970, 1, 1)
                    )
                    points_kv.put()

                Helpers.send_html_email(new_user.rep_email, "Your Application to New Power", "user_signs_up", template_vars)

                attachment_data = {}
                attachment_data["data"] = ["https://storage.googleapis.com" + bucket + "/TempDocs/" + new_user.identifier + "_" + chr(65 + info_dct["agreement_page_count"] - 1) + ".pdf"]
                attachment_data["content_types"] = ["application/pdf"]
                attachment_data["filenames"] = ["W9_I9_Agreement_" + name.replace(" ", "_") + ".pdf"]

                notification_msg1 = "Dear Administrator,\n\nA new user (" +  name + ") has requested access to register with the in-house npfieldapp.appspot.com app. If you would like to approve " + name + ", please visit the following link (must be signed-in):\n\n"
                notification_msg1 += "https://" + self.request.environ["SERVER_NAME"] + "/approve_user/" + new_user.identifier

                notification_entries = Notification.query(
                    ndb.OR
                    (
                        Notification.action_name == "User Registers for App (Email)",
                        Notification.action_name == "User Registers for App (SMS)",
                    )
                )

                form_office = "unknown office"
                offices = OfficeLocation.query(OfficeLocation.is_parent == False)

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
                            Helpers.send_email(person.email_address, "Found talent!", "Talent acquired: " + name.lower() + " from " + city.lower() + ", " + state.lower() + "..." + str(form_office.lower()) + " office")
                        for person in notification_list1:
                            Helpers.send_email(person.email_address, "Approve Access for " + name, notification_msg1, attachment_data)

                gcs.delete(bucket + "/TempDocs/" + usr_dict["identifier"] + "_" + chr(65 + info_dct["agreement_page_count"] - 1) + ".pdf")
                new_user.put()

                self.redirect("/?just_registered=true")

                return

