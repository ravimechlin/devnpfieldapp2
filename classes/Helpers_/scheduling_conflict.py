@staticmethod
def scheduling_conflict(start_dt, end_dt, rep_id_or_rep_identifier, event_identifier="-1"):
    from datetime import date
    from datetime import datetime
    from datetime import timedelta

    ret = {"success": True}
    #return ret

    rep = None
    rep_identifier = rep_id_or_rep_identifier
    if len(rep_id_or_rep_identifier) == 128:
        rep = FieldApplicationUser.first(FieldApplicationUser.identifier == rep_id_or_rep_identifier)
    else:
        rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == rep_id_or_rep_identifier)
        if not rep is None:
            rep_identifier = rep.identifier

    if not rep is None:
        time_dict = {}
        for hour in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]:
            for minute in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]:
                hour_str = str(hour)
                if len(hour_str) == 1:
                    hour_str = "0" + hour_str
                minute_str = str(minute)
                if len(minute_str) == 1:
                    minute_str = "0" + minute_str

                time_dict[hour_str + ":" + minute_str] = "Available"

        day_to_check_floor = datetime(start_dt.year, start_dt.month, start_dt.day, 0, 0, 0)
        day_to_check_ceiling = datetime(start_dt.year, start_dt.month, start_dt.day, 23, 59, 59)
        events = CalendarEvent.query(
            ndb.AND(
                CalendarEvent.start_dt >= day_to_check_floor,
                CalendarEvent.start_dt <= day_to_check_ceiling
            )
        )
        events_cpy = []
        for ev in events:
            events_cpy.append(ev)

        recurring_events = CalendarEvent.query(
            ndb.AND(
                CalendarEvent.repeated == True,
                CalendarEvent.calendar_key == rep_identifier
            )
        )
        for ev in recurring_events:
            iso_weekday = str(start_dt.isoweekday())
            start_dt_cpy2 = day_to_check_floor

            conversion_mapping = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 0}
            day = conversion_mapping[iso_weekday]
            if day in json.loads(ev.repeated_days):
                fake_ev = CalendarEvent(
                    all_day=False,
                    calendar_key=rep_identifier,
                    color=ev.color,
                    details=ev.details,
                    end_dt=datetime(start_dt_cpy2.year, start_dt_cpy2.month, start_dt_cpy2.day, ev.end_dt.hour, ev.end_dt.minute, ev.end_dt.second),
                    event_key=ev.event_key,
                    exception_dates=ev.exception_dates,
                    field_app_identifier=ev.field_app_identifier,
                    google_series_id=ev.google_series_id,
                    identifier=ev.identifier,
                    name=ev.name,
                    owners=ev.owners,
                    repeated_days=ev.repeated_days,
                    start_dt=datetime(start_dt_cpy2.year, start_dt_cpy2.month, start_dt_cpy2.day, ev.start_dt.hour, ev.start_dt.minute, ev.start_dt.second)
                )
                events_cpy.append(fake_ev)


        minute_name_dict = {}
        for ev in events_cpy:
            if not ev.repeated and (ev.calendar_key == rep_identifier) and (event_identifier == "-1" or (not ev.identifier == event_identifier)):
                start_dt2 = datetime(ev.start_dt.year, ev.start_dt.month, ev.start_dt.day, ev.start_dt.hour, ev.start_dt.minute)
                end_dt2 = datetime(ev.end_dt.year, ev.end_dt.month, ev.end_dt.day, ev.end_dt.hour, ev.end_dt.minute)
                start_dt_cpy = datetime(ev.start_dt.year, ev.start_dt.month, ev.start_dt.day, ev.start_dt.hour, ev.start_dt.minute)

                while start_dt_cpy <= end_dt2:
                    hour = start_dt_cpy.hour
                    minute = start_dt_cpy.minute

                    hour_str = str(hour)
                    minute_str = str(minute)

                    if len(hour_str) == 1:
                        hour_str = "0" + hour_str
                    if len(minute_str) == 1:
                        minute_str = "0" + minute_str

                    time_dict[hour_str + ":" + minute_str] = "Taken"
                    minute_name_dict[hour_str + ":" + minute_str] = ev.name
                    start_dt_cpy = start_dt_cpy + timedelta(minutes=1)

        start_dt_cpy = datetime(start_dt.year, start_dt.month, start_dt.day, start_dt.hour, start_dt.minute)
        while start_dt_cpy <= end_dt:
            hour = start_dt_cpy.hour
            minute = start_dt_cpy.minute

            hour_str = str(hour)
            minute_str = str(minute)

            if len(hour_str) == 1:
                hour_str = "0" + hour_str
            if len(minute_str) == 1:
                minute_str = "0" + minute_str

            if time_dict[hour_str + ":" + minute_str] == "Taken":
                ret["success"] = False
                ret["conflicting_event"] = minute_name_dict[hour_str + ":" + minute_str]

            start_dt_cpy = start_dt_cpy + timedelta(minutes=1)

    return ret
