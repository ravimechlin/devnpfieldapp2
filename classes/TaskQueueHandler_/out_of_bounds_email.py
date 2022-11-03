def out_of_bounds_email(self):
    h_p_n = Helpers.pacific_now()
    yesterday_start = datetime(h_p_n.year, h_p_n.month, h_p_n.day, 0, 0, 0)
    yesterday_end = datetime(h_p_n.year, h_p_n.month, h_p_n.day, 23, 59, 59)

    yesterday_start = yesterday_start + timedelta(days=-1)
    yesterday_end = yesterday_end + timedelta(days=-1)

    logs = UserLocationLogItem.query(
        ndb.AND(
            UserLocationLogItem.created >= yesterday_start,
            UserLocationLogItem.created <= yesterday_end
        )
    )

    reps_out_of_bounds = []
    for log in logs:
        if (not log.in_bounds):
            if not log.rep_identifier in reps_out_of_bounds:
                reps_out_of_bounds.append(log.rep_identifier)

    if len(reps_out_of_bounds) > 0:
        email_body = "The following reps were out of bounds yesterday (" + str(yesterday_start.date()) + "):\r\n\r\n"
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(reps_out_of_bounds))
        for rep in reps:
            email_body += (rep.first_name.strip().title() + " " + rep.last_name.strip().title())
            email_body += "\r\n"

        notification = Notification.first(Notification.action_name == "Reps Out of Bounds")
        if not notification is None:
            for p in notification.notification_list:
                Helpers.send_email(p.email_address, "Out of Bounds Reps", email_body)
