def lead_passing_danger(self):
    from datetime import datetime
    from datetime import timedelta


    leads = FieldApplicationEntry.query(
        ndb.AND(
            FieldApplicationEntry.processed == 0,
            FieldApplicationEntry.is_lead == True
        )
    ).fetch(50)

    send_email = False
    now = Helpers.pacific_now()
    for lead in leads:
        if (not lead.archived) and (not lead.save_me):
            if lead.insert_time >= 1516064400000:
                if lead.sp_two_time > now:
                    diff_seconds = (lead.sp_two_time - now).total_seconds()
                    if diff_seconds < 60 * 60 * 6:
                        send_email = True

    if send_email:
        notification = Notification.first(Notification.action_name == "Lead SP2 Passing Danger")
        if not notification is None:
            for person in notification.notification_list:
                Helpers.send_email(person.email_address, "Urgent: Action Required", "One or more leads have not been assigned with an SP2 Time approaching in less than 6 hours")

