def rep_stats_morning_reminder(self):
    from datetime import datetime
    from datetime import timedelta
    now = Helpers.pacific_now()
    day_before = now + timedelta(hours=-24)
    yesterday_start = datetime(day_before.year, day_before.month, day_before.day)
    yesterday_end = datetime(day_before.year, day_before.month, day_before.day, 23, 59, 59)

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= yesterday_start,
            LeaderBoardStat.dt <= yesterday_end
        )
    )

    rep_ids_to_query = ["-1"]
    rep_id_info_dict = {}
    for stat in stats:
        if not stat.rep_id in rep_id_info_dict.keys():
            rep_id_info_dict[stat.rep_id] = {"hks": 0, "abs": 0, "dropped_pins": 0}
        #rep_id_info_dict[stat.rep_id]["hks"] += int(stat.metric_key == "hours_knocked_v2")
        rep_id_info_dict[stat.rep_id]["abs"] += int(stat.metric_key == "leads_acquired")
        rep_id_info_dict[stat.rep_id]["dropped_pins"] += int(stat.metric_key in ["app_stat_CD", "app_stat_R", "app_stat_CB", "app_stat_NQ", "app_stat_NI", "app_stat_AB"])
        if not stat.rep_id in rep_ids_to_query:
            rep_ids_to_query.append(stat.rep_id)

    rep_id_name_dict = {}
    rep_id_phone_dict = {}
    rep_id_rep_identifier_dict = {}
    rep_identifier_rep_id_dict = {}
    reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))
    for rep in reps:
        rep_id_name_dict[rep.rep_id] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
        rep_id_phone_dict[rep.rep_id] = rep.rep_phone
        rep_id_rep_identifier_dict[rep.rep_id] = rep.identifier
        rep_identifier_rep_id_dict[rep.identifier] = rep.rep_id

    hk_data = HKTally.query(
        ndb.AND(
            HKTally.dt >= yesterday_start,
            HKTally.dt <= yesterday_end
        )
    )

    for item in hk_data:
        if item.rep_identifier in rep_identifier_rep_id_dict.keys():
            rep_id = rep_identifier_rep_id_dict[item.rep_identifier]
            if not rep_id in rep_id_info_dict.keys():
                rep_id_info_dict[rep_id] = {"hks": 0, "abs": 0, "dropped_pins": 0}
            rep_id_info_dict[rep_id]["hks"] += item.minutes

    for rep_id in rep_id_info_dict.keys():
        minutes = rep_id_info_dict[rep_id]["hks"]
        hours = float(minutes) / float(60)
        hours = round(hours, 2) 
        rep_id_info_dict[rep_id]["hks"] = hours

    for rep_id in rep_id_info_dict.keys():
        if rep_id_info_dict[rep_id]["hks"] > 0:
            msg = "Hey " + rep_id_name_dict[rep_id] + " - Yesterday you had " + str(rep_id_info_dict[rep_id]["hks"]) + " HKs, dropped " + str(rep_id_info_dict[rep_id]["dropped_pins"]) + " pins, and had " + str(rep_id_info_dict[rep_id]["abs"]) + " ABs. Please contact your solar pro manager if you have questions."
            #Helpers.send_sms(rep_id_phone_dict[rep_id], msg)
