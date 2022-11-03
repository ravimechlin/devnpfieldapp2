def post(self):
    from datetime import datetime
    from datetime import timedelta

    self.response.content_type = "application/json"
    ret_json = {"data": []}

    h_p_t = Helpers.pacific_today()

    start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
    while not start_dt.isoweekday() == 7:
        start_dt = start_dt + timedelta(days=-1)

    start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

    #START DELETE LATER
    
    start_dt = start_dt + timedelta(days=-7)
    end_dt = end_dt + timedelta(days=-7)

    #END DELETE LATER

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= start_dt,
            LeaderBoardStat.dt <= end_dt,
            LeaderBoardStat.metric_key.IN(["data_logger_deployed", "data_logger_retrieved"])
        )
    )

    rep_ids_to_query = ["-1"]
    app_ids_to_query = ["-1"]
    app_identifier_idx_dict = {}
    for stat in stats:
        obj = {}
        obj["dt"] = str(stat.dt).split(".")[0]
        obj["field_app_identifier"] = stat.field_app_identifier
        obj["metric_key"] = stat.metric_key
        obj["rep_id"] = stat.rep_id
        app_identifier_idx_dict[stat.field_app_identifier] = len(ret_json["data"])
        ret_json["data"].append(obj)
        if not stat.rep_id in rep_ids_to_query:
            rep_ids_to_query.append(stat.rep_id)
        if not stat.field_app_identifier in app_ids_to_query:
            app_ids_to_query.append(stat.field_app_identifier)

    rep_id_rep_identifier_dict = {}
    rep_identifier_rep_name_dict = {}
    reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))
    for rep in reps:
        rep_id_rep_identifier_dict[rep.rep_id] = rep.identifier
        rep_identifier_rep_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

    for item in ret_json["data"]:
        item["rep_identifier"] = rep_id_rep_identifier_dict[item["rep_id"]]
        item["rep_name"] = rep_identifier_rep_name_dict[item["rep_identifier"]]

    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    for app_entry in app_entries:
        idx = app_identifier_idx_dict[app_entry.identifier]
        ret_json["data"][idx]["customer_name"] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
        ret_json["data"][idx]["address"] = app_entry.customer_address
        ret_json["data"][idx]["city"] = app_entry.customer_city
        ret_json["data"][idx]["state"] = app_entry.customer_state
        ret_json["data"][idx]["postal"] = app_entry.customer_postal

    cpy = []
    app_ids_found = []

    for item in ret_json["data"]:
        if item["metric_key"] == "data_logger_retrieved":
            cpy.append(item)
            app_ids_found.append(item["field_app_identifier"])

    for item in ret_json["data"]:
        if item["metric_key"] == "data_logger_deployed":
            app_id = item["field_app_identifier"]
            if not app_id in app_ids_found:
                cpy.append(item)

    ret_json["data"] = cpy
    ret_json["data"] = Helpers.bubble_sort(ret_json["data"], "dt")

    self.response.out.write(json.dumps(ret_json))
