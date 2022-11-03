def calendar_event_owners_reminder(self):
    now = Helpers.pacific_now()
    events = []
    if self.request.get("type") == "day_before":
        tomorrow =  now + timedelta(days=1)
        tomorrow1 = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        tomorrow2 = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59)

        events = CalendarEvent.query(
            ndb.AND(
                CalendarEvent.start_dt >= tomorrow1,
                CalendarEvent.start_dt <= tomorrow2
            )
        )

    if self.request.get("type") == "day_of":
        today1 = datetime(now.year, now.month, now.day)
        today2 = datetime(now.year, now.month, now.day, 23, 59, 59)

        events = CalendarEvent.query(
            ndb.AND(
                CalendarEvent.start_dt >= today1,
                CalendarEvent.start_dt <= today2
            )
        )

    for ev in events:
        if ev.calendar_key == "main":        
            if not ev.repeated:
                owners = json.loads(ev.owners)
                xxyy = 25
                    
                for owner in owners:
                    if not owner == "-1":
                        usr = FieldApplicationUser.first(
                            ndb.AND(
                                FieldApplicationUser.current_status == 0,
                                FieldApplicationUser.identifier == owner
                            )
                        )
                        if not usr is None:
                            app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == ev.field_app_identifier)
                            if not app_entry is None or ev.field_app_identifier == "-1":
                                start_str = ev.start_dt.strftime("%I:%M %p")
                                end_str = ev.end_dt.strftime("%I:%M %p")
                                address_str = ""
                                date_str = "Tomorrow"
                                if self.request.get("type") == "day_of":
                                    date_str = "Today"
                                if not app_entry is None:
                                    address_str = "Address: " + app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal + "."
                                sms = ""
                                
                                if not ev.all_day:
                                    sms = "Reminder: " + ev.name + ". " + date_str + "  from " + start_str + " to " + end_str + ". " + address_str
                                else:
                                    sms = "Reminder: " + ev.name + ". " + date_str + " (all day). " + address_str
                                Helpers.send_sms(usr.rep_phone, sms, "+19518015044")

    repeated_events = CalendarEvent.query(CalendarEvent.repeated == True)
    for ev in repeated_events:
        if ev.calendar_key == "main":
            owners = json.loads(ev.owners)
            for owner in owners:    
                if not owner == "-1":
                    usr = FieldApplicationUser.first(
                        ndb.AND(
                            FieldApplicationUser.current_status == 0,
                            FieldApplicationUser.identifier == owner
                        )
                    )
                    if not usr is None:
                        exception_dates = json.loads(ev.exception_dates)
                        exception_dates2 = []
                        for item in exception_dates:
                            dt_vals = item.split("-")
                            dt = date(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                            exception_dates2.append(dt)
                        exception_dates = exception_dates2

                        needle_date = Helpers.pacific_now()
                        if self.request.get("type") == "day_before":
                            needle_date = needle_date + timedelta(days=-1)
                        needle_date = needle_date.date()
                        if not needle_date in exception_dates:
                            repeated_days = json.loads(ev.repeated_days)
                            iso_conversion_mapping = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 0: 7}
                            repeated_days2 = []
                            for item in repeated_days:
                                repeated_days2.append(iso_conversion_mapping[item])
                            repeated_days = repeated_days2

                            iso_weekday = Helpers.pacific_now().isoweekday()
                            if str(self.request.get("type")) == "day_before":
                                iso_weekday = (Helpers.pacific_now() + timedelta(days=1)).isoweekday()

                            if iso_weekday in repeated_days:
                                start_str = ev.start_dt.strftime("%I:%M %p")
                                end_str = ev.end_dt.strftime("%I:%M %p")
                                date_str = "Tomorrow"
                                if self.request.get("type") == "day_of":
                                    date_str = "Today"
                                sms = "Reminder: " + ev.name + ". " + date_str + "  from " + start_str + " to " + end_str + ". "
                                Helpers.send_sms(usr.rep_phone, sms, "+19518015044")

