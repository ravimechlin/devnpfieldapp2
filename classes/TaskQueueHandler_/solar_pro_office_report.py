def solar_pro_office_report(self):
    from datetime import date
    from datetime import datetime
    from datetime import timedelta

    h_p_t = Helpers.pacific_today()
    start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
    while not start_dt.isoweekday() == 7:
        start_dt = start_dt + timedelta(days=-1)

    start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

    start_dt = start_dt + timedelta(days=-7)
    end_dt = end_dt + timedelta(days=-7)

    office_identifier_managers_dict = {}
    managers = FieldApplicationUser.query(FieldApplicationUser.user_type == "solar_pro_manager")
    for manager in managers:
        if manager.current_status == 0:
            if not manager.main_office in office_identifier_managers_dict.keys():
                office_identifier_managers_dict[manager.main_office] = []
            office_identifier_managers_dict[manager.main_office].append({"name": manager.first_name.strip().title() + " " + manager.last_name.strip().title(), "email": manager.rep_email, "identifier": manager.identifier})
    #manually add john martinez in lancaster
    if not "8cd03f5508015a4366aeccd5d4035d21d37441795bb3e4ef16b1d8e54de993bb626a9a935413141ef6c467eaef23743ee791d4520aa1159fb028eb440704ca49" in office_identifier_managers_dict.keys():
        office_identifier_managers_dict["8cd03f5508015a4366aeccd5d4035d21d37441795bb3e4ef16b1d8e54de993bb626a9a935413141ef6c467eaef23743ee791d4520aa1159fb028eb440704ca49"] = []
        office_identifier_managers_dict["8cd03f5508015a4366aeccd5d4035d21d37441795bb3e4ef16b1d8e54de993bb626a9a935413141ef6c467eaef23743ee791d4520aa1159fb028eb440704ca49"].append({"name": "John Martinez", "email": "jmartinez@newpower.net", "identifier": "8b3e1f1c349021ef367cf3c19b516dd5b606f97837b6db5a77e6a43fc4d48c0b6b121151ef90bfc7b5d12dee527f319be76f8caf07d1717ac21e9c91bbf6c508"})

    metric_keys = ["hours_knocked_v2", "app_stat_CD", "app_stat_R", "app_stat_CB", "app_stat_NQ", "app_stat_NI", "app_stat_AB", "app_stat_NH", "leads_acquired", "appointments_kept", "same_week_ab_to_ak"]
    for office_identifier in office_identifier_managers_dict.keys():
        
        users2 = FieldApplicationUser.query(
            ndb.AND(
                FieldApplicationUser.main_office == office_identifier,
                FieldApplicationUser.user_type.IN(["solar_pro", "solar_pro_manager"])
            )
        )
        eligible_rep_ids = []
        for user in users2:
            eligible_rep_ids.append(user.rep_id)
        
        pin_identifiers = []
        users = FieldApplicationUser.query(
            ndb.AND(
                FieldApplicationUser.user_type.IN(["solar_pro", "solar_pro_manager"]),
                FieldApplicationUser.main_office == office_identifier
            )
        )

        rep_id_name_dict = {}
        rep_id_info_dict = {}
        rep_id_rep_identifier_dict = {}
        rep_identifier_rep_id_dict = {}
        for user in users:
            rep_id_name_dict[user.rep_id] = user.first_name.strip().title() + " " + user.last_name.strip().title()
            rep_id_info_dict[user.rep_id] = {}
            rep_id_rep_identifier_dict[user.rep_id] = user.identifier
            rep_identifier_rep_id_dict[user.identifier] = user.rep_id
            rep_id_info_dict[user.rep_id]["HKs"] = 0
            rep_id_info_dict[user.rep_id]["Pins Dropped (NHs omitted)"] = 0
            rep_id_info_dict[user.rep_id]["ABs"] = 0
            rep_id_info_dict[user.rep_id]["AKs"] = 0
            rep_id_info_dict[user.rep_id]["NHs"] = 0
            rep_id_info_dict[user.rep_id]["Same Week AKs"] = 0
            rep_id_info_dict[user.rep_id]["CDs"] = 0

        cd_stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= end_dt,
                LeaderBoardStat.metric_key == "packets_submitted",
                LeaderBoardStat.office_identifier == office_identifier
            )
        )

        cd_app_ids_to_query = ["-1"]
        for stat in cd_stats:
            cd_app_ids_to_query.append(stat.field_app_identifier)

        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(cd_app_ids_to_query))
        for app_entry in app_entries:
            lead_generator = app_entry.lead_generator
            if not lead_generator == "-1":
                #BEOW WAS THE NEW IF STATEMENT
                if lead_generator in rep_identifier_rep_id_dict.keys():
                    rep_id = rep_identifier_rep_id_dict[lead_generator]
                    if rep_id in rep_id_info_dict.keys():
                        rep_id_info_dict[rep_id]["CDs"] += 1

        stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.office_identifier == office_identifier,
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= end_dt,
                LeaderBoardStat.metric_key.IN(metric_keys)
            )
        )

        for stat in stats:
            rep_id = stat.rep_id
            if rep_id in rep_id_info_dict.keys():
                if rep_id in eligible_rep_ids:
                    info_dict = rep_id_info_dict[rep_id]
                    metric_key = stat.metric_key
                    if metric_key == "hours_knocked_v2":
                        info_dict["HKs"] += 1
                    elif metric_key in ["app_stat_CD", "app_stat_R", "app_stat_CB", "app_stat_NQ", "app_stat_NI", "app_stat_AB"]:
                        pin_identifier = stat.pin_identifier
                        if not pin_identifier in pin_identifiers:
                            pin_identifiers.append(pin_identifier)
                            info_dict["Pins Dropped (NHs omitted)"] += 1
                    elif metric_key == "app_stat_NH":
                        info_dict["NHs"] += 1

                    elif metric_key == "leads_acquired":
                        info_dict["ABs"] += 1

                    elif metric_key == "appointments_kept":
                        info_dict["AKs"] += 1
                    
                    elif metric_key == "same_week_ab_to_ak":
                        info_dict["Same Week AKs"] += 1

        data = []
        for rep_id in rep_id_info_dict.keys():
            info_dict = rep_id_info_dict[rep_id]
            tally = 0
            for key in info_dict.keys():
                tally += info_dict[key]
            if tally > 0:
                obj = {}
                obj["Rep Name"] = rep_id_name_dict[rep_id]
                obj["Rep Name Lowered"] =  obj["Rep Name"].lower().replace(" ", "")
                obj["HKs"] = info_dict["HKs"]
                obj["Pins Dropped (NHs omitted)"] = info_dict["Pins Dropped (NHs omitted)"]
                obj["ABs"] = info_dict["ABs"]
                obj["AKs"] = info_dict["AKs"]
                obj["NHs"] = info_dict["NHs"]
                obj["Same Week AKs"] = info_dict["Same Week AKs"]
                obj["CDs"] = info_dict["CDs"]
                result = ""
                if obj["ABs"] > 0:
                    result = float(info_dict["Same Week AKs"]) / float(info_dict["ABs"])
                    result *= float(100)
                    result = int(result)
                    result = str(result)
                    result += "%"
                else:
                    result = "undefined (dawg, can't divide by zero)"
                obj["Same Week AB to AK Percentage"] = result 
                data.append(obj)
        
        data = Helpers.bubble_sort(data, "Rep Name Lowered")
        office_name = ""
        ol = OfficeLocation.first(OfficeLocation.identifier == office_identifier)
        if not ol is None:
            office_name = ol.name
            
        subject = "Solar Pros - Activity Report for " + office_name + " | " + str(start_dt.date()) + " --- " + str(end_dt.date())
        msg = "Hi guys, your report is below:\r\n\r\n"
        for obj in data:
            del obj["Rep Name Lowered"]
            msg += "\r\n"
            msg += "------------------------------"
            msg += "\r\n"
            for key in obj.keys():
                msg += key + " => " + str(obj[key])
                msg += "\r\n"
            msg += "------------------------------"
            msg += "\r\n"
            msg += "============================="
            msg += "\r\n"

        if len(data) > 0:
            ccs = ["reimer@newpower.net", "thomas@newpower.net", "ray@newpower.net"]
            for obj in office_identifier_managers_dict[office_identifier]:
                ccs.append(obj["email"])
            
            Helpers.send_email("archive@newpower.net", subject, msg, None, ccs)
