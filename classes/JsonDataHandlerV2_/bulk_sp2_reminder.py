def bulk_sp2_reminder(self):
    from datetime import datetime

    now = Helpers.pacific_now()
    start_dt = datetime(now.year, now.month, now.day)
    end_dt = datetime(now.year, now.month, now.day, 23, 59, 59)

    events = CalendarEvent.query(
        ndb.AND(
            CalendarEvent.start_dt >= start_dt,
            CalendarEvent.start_dt <= end_dt
        )
    )
    events_cpy = []
    app_ids_to_query = ["-1"]
    rep_ids_to_query = ["-1"]
    for ev in events:
        if ev.event_key == "sp2":
            events_cpy.append(ev)
            app_ids_to_query.append(ev.field_app_identifier)
            rep_ids_to_query.append(ev.calendar_key)

    app_identifier_name_dict = {}
    rep_identifier_name_dict = {}
    save_me_archived_list = []


    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    for app_entry in app_entries:
        app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
        if app_entry.save_me or app_entry.archived:
            save_me_archived_list.append(app_entry.identifier)

    reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
    for rep in reps:
        rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

    events_cpy = Helpers.bubble_sort(events_cpy, "start_dt")

    email_body = "Good morning! Here are today's appointments:\r\n\r\n"

    one_or_more_appointments = False
    for ev in events_cpy:
        if not ev.field_app_identifier in save_me_archived_list:
            one_or_more_appointments = True
            start_hour = ev.start_dt.hour
            am_pm = "AM"
            start_minute = ev.start_dt.minute
            if start_hour >= 12:
                am_pm = "PM"
            if start_hour > 12:
                start_hour -= 12

            start_hour_str = str(start_hour)
            if len(start_hour_str) == 1:
                start_hour_str = "0" + start_hour_str

            start_min_str = str(start_minute)
            if len(start_min_str) == 1:
                start_min_str = "0" + start_min_str

            email_body += app_identifier_name_dict[ev.field_app_identifier] + " / " + rep_identifier_name_dict[ev.calendar_key] + " @ " + start_hour_str + ":" + start_min_str + " " + am_pm + "\r\n"

    if not one_or_more_appointments:
        email_body = "Good morning! There are no SP2 appointments today."
    
    notification = Notification.first(Notification.action_name == "SP2 Daily Summary")
    if not notification is None:
        for p in notification.notification_list:
            Helpers.send_email(p.email_address, "Today's SP2 Summary", email_body)

