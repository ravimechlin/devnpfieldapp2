def quadrant_activity_email(self):
    from datetime import timedelta
    yesterday = (Helpers.pacific_now() + timedelta(hours=-24)).date()
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "area_activity_" + str(yesterday))
    if not kv is None:
        subject = "Area Activity for Yesterday"
        email_body = ""
        data = json.loads(kv.val)
        for item in data:
            email_body += "------------------------"
            email_body += "\r\n"
            email_body += item["msg"]
            email_body += "\r\n"
            email_body += "------------------------"
            email_body += "\r\n\r\n"

        notification = Notification.first(Notification.action_name == "Area Activity")
        if not notification is None:
            for person in notification.notification_list:
                Helpers.send_email(person.email_address, subject, email_body)
