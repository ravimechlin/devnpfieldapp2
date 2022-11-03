def sp_daily_report(self):
    from datetime import datetime
    from datetime import timedelta

    rep_id_hks_dict = {}
    rep_id_yesterday_hks_dict = {}
    
    rep_id_pins_dropped_dict = {}
    rep_id_yesterday_pins_dropped_dict = {}

    rep_id_abs_dict = {}
    rep_id_yesterday_abs_dict = {}

    rep_id_aks_dict = {}
    rep_id_yesterday_aks_dict = {}

    h_p_t = Helpers.pacific_today()

    h_p_n = Helpers.pacific_now()
    one_day_ago = h_p_n + timedelta(days=-1)
    yesterday_start = datetime(one_day_ago.year, one_day_ago.month, one_day_ago.day, 0, 0, 0)
    yesterday_end = datetime(one_day_ago.year, one_day_ago.month, one_day_ago.day, 23, 59, 59)
    
    start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
    while not start_dt.isoweekday() == 7:
        start_dt = start_dt + timedelta(days=-1)

    start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= start_dt,
            LeaderBoardStat.dt <= end_dt
        )
    )

    for stat in stats:
        if not stat.rep_id in rep_id_hks_dict.keys():
            rep_id_hks_dict[stat.rep_id] = 0
        if not stat.rep_id in rep_id_yesterday_hks_dict.keys():
            rep_id_yesterday_hks_dict[stat.rep_id] = 0

        rep_id_hks_dict[stat.rep_id] += int(stat.metric_key == "hours_knocked_v2")
        rep_id_yesterday_hks_dict[stat.rep_id] += int(stat.metric_key == "hours_knocked_v2" and stat.dt >= yesterday_start and stat.dt <= yesterday_end)




        if not stat.rep_id in rep_id_pins_dropped_dict.keys():            
            rep_id_pins_dropped_dict[stat.rep_id] = 0

        if not stat.rep_id in rep_id_yesterday_pins_dropped_dict.keys():
            rep_id_yesterday_pins_dropped_dict[stat.rep_id] = 0

        rep_id_pins_dropped_dict[stat.rep_id] += int("app_stat" in stat.metric_key)
        rep_id_yesterday_pins_dropped_dict[stat.rep_id] += int("app_stat" in stat.metric_key and stat.dt >= yesterday_start and stat.dt <= yesterday_end)



        if not stat.rep_id in rep_id_abs_dict.keys():
            rep_id_abs_dict[stat.rep_id] = 0

        if not stat.rep_id in rep_id_yesterday_abs_dict.keys():
            rep_id_yesterday_abs_dict[stat.rep_id] = 0

        rep_id_abs_dict[stat.rep_id] += int(stat.metric_key == "leads_acquired")
        rep_id_yesterday_abs_dict[stat.rep_id] += int(stat.metric_key == "leads_acquired" and stat.dt >= yesterday_start and stat.dt <= yesterday_end)


        if not stat.rep_id in rep_id_aks_dict.keys():
            rep_id_aks_dict[stat.rep_id] = 0

        if not stat.rep_id in rep_id_yesterday_aks_dict.keys():
            rep_id_yesterday_aks_dict[stat.rep_id] = 0

        rep_id_aks_dict[stat.rep_id] += int(stat.metric_key == "appointments_kept")
        rep_id_yesterday_aks_dict[stat.rep_id] += int(stat.metric_key == "appointments_kept" and stat.dt >= yesterday_start and stat.dt <= yesterday_end)

    rep_id_name_dict = {}
    rep_id_phone_dict = {}
    rep_ids_to_query = ["-1"]
    users = FieldApplicationUser.query(FieldApplicationUser.user_type.IN(["solar_pro", "solar_pro_manager"]))
    for user in users:
        if "solar_pro" in user.user_type and user.current_status == 0:
            rep_ids_to_query.append(user.rep_id)
            rep_id_name_dict[user.rep_id] = user.first_name.strip().title() + " " + user.last_name.strip().title()
            rep_id_phone_dict[user.rep_id] = user.rep_phone

            if not user.rep_id in rep_id_abs_dict.keys():
                rep_id_abs_dict[user.rep_id] = 0
            if not user.rep_id in rep_id_yesterday_abs_dict.keys():
                rep_id_yesterday_abs_dict[user.rep_id] = 0

            if not user.rep_id in rep_id_aks_dict.keys():
                rep_id_aks_dict[user.rep_id] = 0
            if not user.rep_id in rep_id_yesterday_aks_dict.keys():
                rep_id_yesterday_aks_dict[user.rep_id] = 0

            if not user.rep_id in rep_id_hks_dict.keys():
                rep_id_hks_dict[user.rep_id] = 0
            if not user.rep_id in rep_id_yesterday_hks_dict.keys():
                rep_id_yesterday_hks_dict[user.rep_id] = 0

            if not user.rep_id in rep_id_pins_dropped_dict.keys():
                rep_id_pins_dropped_dict[user.rep_id] = 0
            if not user.rep_id in rep_id_yesterday_pins_dropped_dict.keys():
                rep_id_yesterday_pins_dropped_dict[user.rep_id] = 0

    for rep_id in rep_id_name_dict.keys():
        try:
            msg = "Hey " + rep_id_name_dict[rep_id] + ":\n\nHere are your stats from yesterday...\n\nHKs: " + str(rep_id_yesterday_hks_dict[rep_id]) + ", Pins Dropped: " + str(rep_id_yesterday_pins_dropped_dict[rep_id]) + ", ABs: " +  str(rep_id_yesterday_abs_dict[rep_id]) + ", AKs: " + str(rep_id_yesterday_aks_dict[rep_id]) + "."
            msg += ".\n\nFor the week you have: " + str(rep_id_hks_dict[rep_id]) + " HKs, " + str(rep_id_pins_dropped_dict[rep_id]) + " pins dropped, " + str(rep_id_abs_dict[rep_id]) + " ABs, and " + str(rep_id_aks_dict[rep_id]) + " AKs."
            Helpers.send_sms(rep_id_phone_dict[rep_id], msg)
        except:
            y = "y"

        

        

