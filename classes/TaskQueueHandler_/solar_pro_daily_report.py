def solar_pro_daily_report(self):
    now = Helpers.pacific_now()
    yesterday = now + timedelta(days=-1)
    yesterday_start = datetime(yesterday.year, yesterday.month, yesterday.day)
    yesterday_end = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= yesterday_start,
            LeaderBoardStat.dt <= yesterday_end,
            LeaderBoardStat.metric_key.IN(["app_stat_clockins", "leads_acquired", "app_stat_CD", "app_stat_R", "app_stat_CB", "app_stat_NQ", "app_stat_NI", "app_stat_AB", "app_stat_NH"])
        )
    )

    rep_ids_to_query = ["-1"]
    rep_id_info_dict = {}
    for stat in stats:
        if not stat.rep_id in rep_id_info_dict.keys():
            rep_id_info_dict[stat.rep_id] = {"rep_id": stat.rep_id, "clock_in": datetime(1970, 1, 1), "last_pin": datetime(1970, 1, 1), "HKs": 0, "ABs": 0, "Pins": 0, "NHs": 0}
        if stat.metric_key == "app_stat_clockins":
            rep_id_info_dict[stat.rep_id]["clock_in"] = stat.dt

        if stat.metric_key in ["app_stat_CD", "app_stat_R", "app_stat_CB", "app_stat_NQ", "app_stat_NI", "app_stat_AB", "app_stat_NH"]:
            rep_id_info_dict[stat.rep_id]["Pins"] += 1 * int(not (stat.metric_key == "app_stat_NH"))
            rep_id_info_dict[stat.rep_id]["NHs"] += int(stat.metric_key == "app_stat_NH")
            if stat.dt > rep_id_info_dict[stat.rep_id]["last_pin"]:
                rep_id_info_dict[stat.rep_id]["last_pin"] = stat.dt

        if stat.metric_key == "leads_acquired":
            rep_id_info_dict[stat.rep_id]["ABs"] += 1

    rep_ids_to_query = ["-1"]
    for rep_id in rep_id_info_dict.keys():
        rep_ids_to_query.append(rep_id)

    rep_id_office_dict = {}
    office_ids_to_query = ["-1"]
    reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))
    rep_id_rep_identifier_dict = {}
    rep_identifier_rep_id_dict = {}
    for rep in reps:
        rep_id_info_dict[rep.rep_id]["user_type"] = rep.user_type
        rep_id_info_dict[rep.rep_id]["name"] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
        if rep.user_type == "solar_pro_manager":
            rep_id_info_dict[rep.rep_id]["name"] += " SPM"
        rep_id_info_dict[rep.rep_id]["name_lowered"] = rep_id_info_dict[rep.rep_id]["name"].lower()
        rep_id_office_dict[rep.rep_id] = rep.main_office
        office_ids_to_query.append(rep.main_office)
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
                rep_id_info_dict[rep_id] = {"rep_id": rep_id, "clock_in": datetime(1970, 1, 1), "last_pin": datetime(1970, 1, 1), "HKs": 0, "ABs": 0, "Pins": 0}

            rep_id_info_dict[rep_id]["HKs"] += item.minutes

    for rep_id in rep_id_info_dict.keys():
        minutes = rep_id_info_dict[rep_id]["HKs"]
        hours = minutes / float(60)
        hours = round(hours, 2)
        rep_id_info_dict[rep_id]["HKs"] = hours

    office_identifier_name_dict = {}
    offices = OfficeLocation.query(OfficeLocation.identifier.IN(office_ids_to_query))
    for office in offices:
        office_identifier_name_dict[office.identifier] = office.name

    solar_pro_managers_list = []
    for rep_id in rep_id_info_dict.keys():
        if rep_id_info_dict[rep_id]["user_type"] == "solar_pro_manager":
            solar_pro_managers_list.append(rep_id_info_dict[rep_id])

    solar_pros_list = []
    for rep_id in rep_id_info_dict.keys():
        if rep_id_info_dict[rep_id]["user_type"] == "solar_pro":
            solar_pros_list.append(rep_id_info_dict[rep_id])

    combined = solar_pro_managers_list + solar_pros_list

    office_identifier_list_dict = {}
    for item in combined:
        r_id = item["rep_id"]
        office_identifier = rep_id_office_dict[r_id]
        if not office_identifier in office_identifier_list_dict.keys():
            office_identifier_list_dict[office_identifier] = []
        office_identifier_list_dict[office_identifier].append(item)

    subject = "Yesterday's SP Digest - " + str(yesterday_start.date())
    msg = "Hi guys, report is below....\r\n\r\n"

    for office_identifier in office_identifier_list_dict.keys():
        lst = office_identifier_list_dict[office_identifier]
        lst_sorted = Helpers.bubble_sort(lst, "name_lowered")

        combined2 = []
        for item in lst_sorted:
            if item["user_type"] == "solar_pro_manager":
                combined2.append(item)
        for item in lst_sorted:
            if item["user_type"] == "solar_pro":
                combined2.append(item)

        name = office_identifier_name_dict[office_identifier]
        msg += name
        msg += "\r\n"
        msg += "========================================\r\n"

        for item2 in combined2:
            if not item2["name"] == "Charly Chavez":
                msg += item2["name"]
                msg += " => "

                data_items = ["Clock In: " + item2["clock_in"].strftime("%I:%M %p")]
                data_items.append("Last Pin: " + item2["last_pin"].strftime("%I:%M %p"))
                data_items.append("HKs: " + str(item2["HKs"]))
                data_items.append("ABs: " + str(item2["ABs"]))
                data_items.append("Non NH Pins: " + str(item2["Pins"]))
                data_items.append("NH Pins: " + str(item2["NHs"]))
                msg += " | ".join(data_items)
                msg += "\r\n"
        msg += "\r\n\r\n"

    ccs = []
    notification = Notification.first(Notification.action_name == "Solar Pro Daily Digest")
    if not notification is None:
        for p in notification.notification_list:
            ccs.append(p.email_address)

    Helpers.send_email("ray@newpower.net", subject, msg, None, ccs)

    
