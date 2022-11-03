def post(self, keyy):
    from google.appengine.api import app_identity
    approve_action = self.request.get("approve_action")
    user_identifier = self.request.get("user_identifier")
    user_office = self.request.get("user_office")

    users = FieldApplicationUser.query(FieldApplicationUser.identifier == user_identifier)
    pending_user = None
    for user in users:
        pending_user = user

    if not pending_user is None:
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pending_registrations")
        if not kv is None:
            lst = json.loads(kv.val)
            cpy = []
            for item in lst:
                if not item == user_identifier:
                    cpy.append(item)

            kv.val = json.dumps(cpy)
            kv.put()
        user_email = pending_user.rep_email
        user_type = pending_user.user_type
        user_first = pending_user.first_name
        user_last = pending_user.last_name
        user_rep_id = pending_user.rep_id

        name = user_first + " " + user_last

        template_vars = {}
        template_vars["name"] = name
        template_vars["repid"] =  user_rep_id
        template_vars["email"] = user_email

        template_name = "user_approved"
        
        if approve_action == "drop":
            u = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("user_identifier"))
            if not u is None:
                u.key.delete()

        if approve_action == "deny":
            template_name = "user_denied"
    
            signing_url = "https://" + app_identity.get_application_id() + ".appspot.com/sign/" + pending_user.identifier
            if user_type == "super" or user_type == "solar_pro":
                signing_url = signing_url + "?bundle_key=w2_employee_docs"

            emails = [user_email]
            notification = Notification.first(Notification.action_name == "Registration Rejected")
            if not notification is None:
                for p in notification.notification_list:
                   emails.append(p.email_address)

            for e in emails:
                Helpers.send_email(e, "Action Needed for Field App Access", "Hello " + user_first + " " + user_last + ", your signature was rejected on the new power registration documents.  Please take a minute and re-sign the documents by clicking the link below:\r\n\r\n" + signing_url)

            self.response.content_type = "text/plain"
            self.response.out.write("A new signing url went out to the following list of email addresses:\r\n\r\n" + "\r\n".join(emails))
            return
            
        if approve_action == "approve":

            #try:
                #Helpers.grant_box_collaboration(user_email, user_type)
            #except:
                #nada = "nada"

            form_office = None

            office_locations = OfficeLocation.query(OfficeLocation.parent_identifier != "n/a")
            final_ol = None
            for office_location in office_locations:
                if office_location.identifier == user_office:
                    form_office = office_location.name
                    final_ol = office_location

            logging.info("here2")
            if not form_office is None:
                logging.info("here")
                sales_rabbit_id = "-1"
                if 10 == 10:
                    if final_ol.sales_rabbit_id > -1 and final_ol.sales_rabbit_area_id > -1:
                        sales_rabbit_id = Helpers.grant_sales_rabbit_access(user_email, user_first, user_last, form_office, final_ol)
                else:
                    nada2 = "nada2"

                user_update = pending_user

                user_update.sales_rabbit_id = int(sales_rabbit_id)
                user_update.current_status = 0
                user_update.registration_date = Helpers.pacific_today()
                user_update.put()

                Helpers.create_birthdays_for_user(user_update)

                d = UserDebt.first(UserDebt.field_app_identifier == user_update.identifier)
                if d is None:
                    debt = UserDebt(
                        identifier=Helpers.guid(),
                        field_app_identifier=user_update.identifier,
                        total=float(0),
                        items="[]",
                        modified=datetime(1970, 1, 1)
                    )
                    debt.put()

                write_retry_params = gcs.RetryParams(backoff_factor=1.1)
                #create the user's default profile pictures

                gcs_file1 = GCSLockedFile("/Images/default.jpg")
                bytes1 = gcs_file1.read()
                gcs_file2 = GCSLockedFile("/Images/default_thumb.jpg")
                bytes2 = gcs_file2.read()

                bucket_name = os.environ.get(
                    'BUCKET_NAME',
                    app_identity.get_default_gcs_bucket_name()
                )
                bucket = '/' + bucket_name
                write_retry_params = gcs.RetryParams(backoff_factor=1.1)

                if not bytes1 is None:
                    filename = bucket + "/Images/ProfilePictures/Full/" + user_update.identifier + ".jpg"

                    gcs_file1 = gcs.open(
                        filename,
                        'w',
                        content_type="image/jpeg",
                        options={
                            'x-goog-meta-foo': 'foo',
                            'x-goog-meta-bar': 'bar',
                            'x-goog-acl': 'public-read',
                            'cache-control': 'no-cache'
                        },
                        retry_params=write_retry_params)

                    gcs_file1.write(bytes1)
                    gcs_file1.close()

                if not bytes2 is None:
                    filename = bucket + "/Images/ProfilePictures/Thumb/" + user_update.identifier + ".jpg"

                    gcs_file2 = gcs.open(
                        filename,
                        'w',
                        content_type="image/jpeg",
                        options={
                            'x-goog-meta-foo': 'foo',
                            'x-goog-meta-bar': 'bar',
                            'x-goog-acl': 'public-read',
                            'cache-control': 'no-cache'
                        },
                        retry_params=write_retry_params)

                    gcs_file2.write(bytes2)
                    gcs_file2.close()





                recipient = user_update.identifier
                ol = OfficeLocation.first(OfficeLocation.identifier == user_update.main_office)
                users2 = FieldApplicationUser.query(
                    ndb.AND
                    (
                        FieldApplicationUser.current_status == 0,
                        FieldApplicationUser.main_office == self.request.get("office")
                    )
                )
                if not ol is None:
                    o_data = ol.get_override_data()
                    o_data["recipients"].append(recipient)
                    recipients_cpy = []
                    for item in o_data["recipients"]:
                        if not item in recipients_cpy:
                            recipients_cpy.append(item)
                    o_data["recipients"] = recipients_cpy
                    for user2 in users2:
                        if not user2.identifier in o_data["yielders"]:
                            o_data["yielders"].append(user2.identifier)
                        if not user2.identifier in o_data["data"].keys():
                            o_data["data"][user2.identifier] = []
                        o_data["data"][user2.identifier].append({"identifier": recipient, "amount": "0.00"})

                    
                    yielders_cpy = []
                    for item in o_data["yielders"]:
                        if not item in yielders_cpy:
                            yielders_cpy.append(item)
                    o_data["yielders"] = yielders_cpy

                    for key in o_data["data"].keys():
                        lst = o_data["data"][key]
                        lst_cpy = []
                        recipients_found = []
                        for item in lst:
                            if not item["identifier"] in recipients_found:
                                lst_cpy.append(item)
                        o_data["data"][key] = lst_cpy
                    
                    ol.set_override_data(o_data)

                settings_option = {}
                settings_option["new_customer_note"] = {}
                settings_option["new_customer_note"]["sms"] = True
                settings_option["new_customer_note"]["email"] = True
                f1 = GCSLockedFile("/ApplicationSettings/UserSettings/Notifications/" + user.identifier + ".json")
                f1.write(json.dumps(settings_option), "text/plain", "public-read")
                Helpers.send_html_email(user_email, "Your Application to New Power", template_name, template_vars)
                #Helpers.provision_google_apps_account(user_email, user_first, user_last)

    self.redirect("/")
