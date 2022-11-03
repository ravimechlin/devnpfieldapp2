def get_sp2_events_for_rep(self):
    from datetime import datetime
    from datetime import timedelta

    self.response.content_type = "application/json"
    ret_json = {"events": []}
    app_ids_to_query = ["-1"]
    field_app_identifier_idx_dict = {}


    now = Helpers.pacific_now()
    now = datetime(now.year, now.month, now.day)    
    min_dt = Helpers.pacific_now() + timedelta(days=-30)
    max_dt = datetime(now.year, now.month, now.day, 23, 59, 59) + timedelta(days=30)

    fetch_app_entries = True

    if len(str(self.request.get("start_dt"))) == 10:
        start_dt_vals = self.request.get("start_dt").split("-")
        min_dt = datetime(int(start_dt_vals[0]), int(start_dt_vals[1]), int(start_dt_vals[2]))

        end_dt_vals = self.request.get("end_dt").split("-")
        max_dt = datetime(int(end_dt_vals[0]), int(end_dt_vals[1]), int(end_dt_vals[2]), 23, 59, 59)

        fetch_app_entries = False


    rep = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not rep is None:
        events = CalendarEvent.query(
            ndb.AND(
                CalendarEvent.start_dt >= min_dt,
                CalendarEvent.start_dt <= max_dt,
                CalendarEvent.calendar_key == self.request.get("identifier")
            )
        )
        cnt = 0
        for ev in events:
            if ev.calendar_key == self.request.get("identifier") and (not ev.repeated):                
                e_dt = ev.end_dt + timedelta(minutes=1)
                obj = {"name": ev.name}
                obj["identifier"] = ev.identifier
                obj["field_app_identifier"] = ev.field_app_identifier
                obj["phone"] = None
                obj["address"] = None
                obj["start_dt"] = str(ev.start_dt).split(".")[0]
                obj["end_dt"] = str(e_dt).split(".")[0]
                obj["ab_call"] = False
                obj["repeated"] = False
                ret_json["events"].append(obj)
                app_ids_to_query.append(ev.field_app_identifier)
                field_app_identifier_idx_dict[ev.field_app_identifier] = cnt
                cnt += 1
        
        archived_and_save_mes_list = []
        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        for app_entry in app_entries:
            ret_json["events"][field_app_identifier_idx_dict[app_entry.identifier]]["phone"] = Helpers.format_phone_number(app_entry.customer_phone)
            ret_json["events"][field_app_identifier_idx_dict[app_entry.identifier]]["address"] = app_entry.customer_address + "\n" + app_entry.customer_city + ", " + app_entry.customer_state + "\n" + app_entry.customer_postal
            if app_entry.archived or app_entry.save_me:
                archived_and_save_mes_list.append(app_entry.identifier)


        if fetch_app_entries:
            stats = LeaderBoardStat.query(
                ndb.AND(
                    LeaderBoardStat.metric_key == "ab_with_call",
                    LeaderBoardStat.dt >= min_dt,
                    LeaderBoardStat.dt <= max_dt
                )
            )
            for stat in stats:
                if stat.field_app_identifier in app_ids_to_query:
                    ret_json["events"][field_app_identifier_idx_dict[stat.field_app_identifier]]["ab_call"] = True

        ret_json["repeated_events"] = []
        repeated_events = CalendarEvent.query(
            ndb.AND(
                CalendarEvent.calendar_key == self.request.get("identifier"),
                CalendarEvent.repeated == True
            )
        )
        for ev2 in repeated_events:
            obj = {"name": ev2.name}
            obj["identifier"] = ev2.identifier
            obj["phone"] = None
            obj["address"] = None
            
            start_hour = str(ev2.start_dt.hour)
            if len(start_hour) == 1:
                start_hour = "0" + start_hour
            start_min = str(ev2.start_dt.minute)
            if len(start_min) == 1:
                start_min = "0" + start_min
            obj["start_dt"] = start_hour + ":" + start_min

            end_hour = str(ev2.end_dt.hour)
            if len(end_hour) == 1:
                end_hour = "0" + end_hour
            end_min = str(ev2.end_dt.minute)
            if len(end_min) == 1:
                end_min = "0" + end_min
            obj["end_dt"] = end_hour + ":" + end_min
            obj["repeated"] = True
            obj["dow"] = ev2.repeated_days

            ret_json["repeated_events"].append(obj)

    cpy = []
    for ev in ret_json["events"]:
        append = True
        if "field_app_identifier" in ev.keys():
            if ev["field_app_identifier"] in archived_and_save_mes_list:
                append = False
        if append:
            cpy.append(ev)

    ret_json["events"] = cpy

    self.response.out.write(json.dumps(ret_json))
