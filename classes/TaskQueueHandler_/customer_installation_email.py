def customer_installation_email(self):
    from datetime import date
    from datetime import datetime
    from datetime import timedelta

    pp_subs = PerfectPacketSubmission.query(
        ndb.AND(
            PerfectPacketSubmission.archived == False,
            PerfectPacketSubmission.save_me == False
        )
    )

    f1 = GCSLockedFile("/CustomerEmailTemplates/Installation.subject")
    f2 = GCSLockedFile("/CustomerEmailTemplates/Installation.txt")

    subject = f1.read()
    msg = f2.read()

    f1.unlock()
    f2.unlock()

    for pp_sub in pp_subs:
        if (not pp_sub.archived) and (not pp_sub.save_me):
            tomorrow = Helpers.pacific_now() + timedelta(days=1)
            tomorrow = tomorrow.date()
            info = json.loads(pp_sub.extra_info)
            if "project_management_checkoffs" in info.keys():
                #Helpers.send_email("rnirnber@gmail.com", "here", "here1")
                if "install" in info["project_management_checkoffs"].keys():
                    #Helpers.send_email("rnirnber@gmail.com", "here", "here2")
                    if "date" in info["project_management_checkoffs"]["install"].keys():
                        #Helpers.send_email("rnirnber@gmail.com", "here", "here3")
                        if isinstance(info["project_management_checkoffs"]["install"]["date"], str) or isinstance(info["project_management_checkoffs"]["install"]["date"], unicode):
                            #Helpers.send_email("rnirnber@gmail.com", "here", "here4")
                            if "-" in info["project_management_checkoffs"]["install"]["date"]:
                                dt_vals = info["project_management_checkoffs"]["install"]["date"].split("-")
                                dt = date(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                                if dt == tomorrow:
                                    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == pp_sub.field_application_identifier)
                                    if not app_entry is None:
                                        html = Helpers.fill_email_template(pp_sub, app_entry, msg)
                                        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "install_email_sent_" + pp_sub.field_application_identifier)
                                        if kv is None:
                                            kv = KeyValueStoreItem(
                                                identifier=Helpers.guid(),
                                                keyy="install_email_sent_" + pp_sub.field_application_identifier,
                                                val=str(Helpers.pacific_today()),
                                                expiration=datetime(1970, 1, 1)
                                            )
                                            kv.put()
                                            Helpers.send_customer_email(html, subject, app_entry.customer_email, "'Installation' email was sent out.", pp_sub.field_application_identifier)

