def time_slots_for_office(self):
    from datetime import datetime
    from datetime import timedelta
    import json

    office_identifier = self.request.get("identifier")
    special_minutes_offset = Helpers.get_sp2_special_offset(office_identifier)

    rs = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.main_office == office_identifier,
            FieldApplicationUser.current_status == 0,
            FieldApplicationUser.accepts_leads == True
        )
    )

    minutes_off = Helpers.get_sp2_special_offset(office_identifier)

    reps = []
    rep_identifiers = ["-1"]
    for r in rs:
        if (not r.user_type == "super") and (not r.user_type == "solar_pro") and (not r.user_type == "solar_pro_manager"):
            reps.append(r)
            rep_identifiers.append(r.identifier)

    rep_identifier_slot_dict = {}
    for rep in reps:
        hour = 9
        minute = 0

        while hour <= 23:
            if not rep.identifier in rep_identifier_slot_dict.keys():
                rep_identifier_slot_dict[rep.identifier] = {}
            hour_str = str(hour)
            if len(hour_str) == 1:
                hour_str = "0" + hour_str
            min_str = str(minute)
            if len(min_str) == 1:
                min_str = "0" + min_str
            rep_identifier_slot_dict[rep.identifier][hour_str + ":" + min_str] = "Available"
            minute += 1
            if minute == 60:
                minute = 0
                hour += 1

    dt_vals = self.request.get("dt").split("-")
    start_dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
    end_dt = datetime(start_dt.year, start_dt.month, start_dt.day, 23, 59, 59)
    start_dt_cpy = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))

    events = CalendarEvent.query(
        ndb.AND(
            CalendarEvent.start_dt >= start_dt,
            CalendarEvent.start_dt <= end_dt
        )
    )
    events_cpy = []
    for ev in events:
        if ev.calendar_key in rep_identifiers:
            events_cpy.append(ev)

    repeated_events = CalendarEvent.query(
        ndb.AND(
            CalendarEvent.repeated == True,
            CalendarEvent.calendar_key.IN(rep_identifiers)
        )
    )

    for ev in repeated_events:
        event_weekdays = json.loads(ev.repeated_days)
        events_weekdays_cpy = []
        for weekday in event_weekdays:
            wd = weekday
            if wd == 0:
                wd = 7
            events_weekdays_cpy.append(wd)        
        dt = start_dt.date()
        if dt.isoweekday() in events_weekdays_cpy:
            fake_ev = CalendarEvent()
            fake_ev.calendar_key = ev.calendar_key
            fake_ev.start_dt = datetime(dt.year, dt.month, dt.day, ev.start_dt.hour, ev.start_dt.minute)
            fake_ev.end_dt = datetime(dt.year, dt.month, dt.day, ev.end_dt.hour, ev.end_dt.minute)
            events_cpy.append(fake_ev)

    for ev in events_cpy:
        rep_identifier = ev.calendar_key
        start_dt = datetime(ev.start_dt.year, ev.start_dt.month, ev.start_dt.day, ev.start_dt.hour, ev.start_dt.minute)
        while start_dt <= ev.end_dt:
            hour = start_dt.hour
            minute = start_dt.minute
            hour_str = str(hour)
            if len(hour_str) == 1:
                hour_str = "0" + hour_str
            min_str = str(minute)
            if len(min_str) == 1:
                min_str = "0" + min_str
            rep_identifier_slot_dict[rep_identifier][hour_str + ":" + min_str] = "Taken"
            start_dt = start_dt + timedelta(minutes=1)

    #Helpers.send_email("rnirnber@gmail.com", "debugging", json.dumps(rep_identifier_slot_dict))
    hours_available = []
    for h in [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
        for rep_identifier in rep_identifier_slot_dict.keys():
            available_minutes = 0
            start_dt = datetime(start_dt_cpy.year, start_dt_cpy.month, start_dt_cpy.day, h, 0, 0)
            end_dt = start_dt + timedelta(minutes=119 - minutes_off)
            while start_dt <= end_dt:
                hour = start_dt.hour
                minute = start_dt.minute
                hour_str = str(hour)
                if len(hour_str) == 1:
                    hour_str = "0" + hour_str
                min_str = str(minute)
                if len(min_str) == 1:
                    min_str = "0" + min_str

                if rep_identifier_slot_dict[rep_identifier][hour_str + ":" + min_str] ==  "Available":
                    available_minutes += 1
                start_dt = start_dt + timedelta(minutes=1)

            if available_minutes == 120 - special_minutes_offset:
                if not h in hours_available:
                    hours_available.append(h)
    
    self.response.content_type = "application/json"
    self.response.out.write(json.dumps(hours_available))
    #Helpers.send_email("rnirnber@gmail.com", "dict", json.dumps(rep_identifier_slot_dict))
