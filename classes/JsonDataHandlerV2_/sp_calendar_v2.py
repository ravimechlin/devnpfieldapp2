def sp_calendar_v2(self):
    self.response.content_type = "application/json"
    #ret_json = {"appointments": []}
    ret_json = {"events": []}
    events = CalendarEvent.query(
        ndb.OR(
            ndb.AND(
                CalendarEvent.calendar_key == self.request.get("identifier"),
                CalendarEvent.start_dt >= Helpers.pacific_now() + timedelta(days=-30)
            ),
            ndb.AND(
                CalendarEvent.calendar_key == self.request.get("identifier"),
                CalendarEvent.repeated == True
            )
        )
    )

    app_ids_to_query = ["-2"]
    app_identifier_idx_dict = {}
    events_cpy = []
    for ev in events:        
        events_cpy.append(ev)
        if not ev.repeated:
            obj = {}
            obj["identifier"] = ev.identifier
            obj["field_app_identifier"] = ev.field_app_identifier
            obj["event_key"] = ev.event_key
            obj["name"] = ev.name
            obj["repeated"] = False
            obj["start_dt"] = str(ev.start_dt).split(".")[0]
            obj["end_dt"] = str(ev.end_dt).split(".")[0]
            obj["details"] = ev.details
            if len(obj["field_app_identifier"]) == 128:
                app_ids_to_query.append(ev.field_app_identifier)
                app_identifier_idx_dict[ev.field_app_identifier] = len(ret_json["events"])

            ret_json["events"].append(obj)

    now = Helpers.pacific_now()
    thirty_days_ago = now + timedelta(days=-30)
    thirty_days_ahead = now + timedelta(days=30)
    dt_mapping = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "0": 7}
    for ev in events_cpy:
        if ev.repeated:
            dt = datetime(thirty_days_ago.year, thirty_days_ago.month, thirty_days_ago.day, thirty_days_ago.hour, thirty_days_ago.minute, thirty_days_ago.second)
            while dt < thirty_days_ahead:
                repeated_days = json.loads(ev.repeated_days)
                for day in repeated_days:
                    dt_str = str(day)
                    num_mapped = dt_mapping[dt_str]

                    if num_mapped == dt.isoweekday():
                        obj = {}
                        obj["identifier"] = ev.identifier
                        obj["field_app_identifier"] = ev.field_app_identifier
                        obj["event_key"] = ev.event_key
                        obj["name"] = ev.name
                        obj["repeated"] = False
                        start_dt_modified = datetime(dt.year, dt.month, dt.day, ev.start_dt.hour, ev.start_dt.minute, ev.start_dt.second)
                        obj["start_dt"] = str(start_dt_modified).split(".")[0]
                        end_dt_modified = datetime(dt.year, dt.month, dt.day, ev.end_dt.hour, ev.end_dt.minute, ev.end_dt.second)
                        obj["end_dt"] = str(end_dt_modified).split(".")[0]
                        obj["details"] = ev.details

                        ret_json["events"].append(obj)

                dt = dt + timedelta(days=1)

    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    for app_entry in app_entries:
        identifier = app_entry.identifier
        idx = app_identifier_idx_dict[identifier]
        name = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
        ret_json["events"][idx]["name"] = name + " - SP2" 
        ret_json["events"][idx]["details"] = "Appointment with " + name + "\n" + app_entry.customer_address + "\n" + app_entry.customer_city + ", " + app_entry.customer_state + "\n" + app_entry.customer_postal + "\n" + Helpers.format_phone_number(app_entry.customer_phone)

    self.response.out.write(json.dumps(ret_json))

