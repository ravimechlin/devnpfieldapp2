def converted_abs_aks(self):
    h_p_t = Helpers.pacific_today()

    start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
    while not start_dt.isoweekday() == 7:
        start_dt = start_dt + timedelta(days=-1)

    start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

    start_dt = start_dt + timedelta(days=-7)
    end_dt = end_dt + timedelta(days=-7)

    ab_stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= start_dt,
            LeaderBoardStat.dt <= end_dt,
            LeaderBoardStat.metric_key == "leads_acquired"
        )
    )

    app_ids_to_query = ["-1"]
    app_identifier_dt_dict = {}
    app_identifier_rep_id_dict = {}
    app_identifier_stat_identifier_dict = {}
    stat_identifier_app_identifier_dict = {}
    ab_stats_cpy = []
    for stat in ab_stats:
        ab_stats_cpy.append(stat)
        app_ids_to_query.append(stat.field_app_identifier)
        app_identifier_dt_dict[stat.field_app_identifier] = stat.dt
        app_identifier_stat_identifier_dict[stat.field_app_identifier] = stat.identifier
        stat_identifier_app_identifier_dict[stat.identifier] = stat.field_app_identifier
        app_identifier_rep_id_dict[stat.field_app_identifier] = stat.rep_id

    ak_stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= start_dt,
            LeaderBoardStat.dt <= end_dt,
            LeaderBoardStat.metric_key == "appointments_kept"
        )
    )

    app_identifier_lead_generator_dict = {}
    app_identifier_name_dict = {}
    app_identifier_rep_id_dict = {}
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    rep_identifiers_to_query = ["-1"]
    for app_entry in app_entries:
        app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
        app_identifier_lead_generator_dict[app_entry.identifier] = app_entry.lead_generator
        app_identifier_rep_id_dict[app_entry.identifier] = app_entry.rep_id
        rep_identifiers_to_query.append(app_entry.lead_generator)

    rep_identifier_rep_id_dict = {}
    reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_identifiers_to_query))
    for rep in reps:
        rep_identifier_rep_id_dict[rep.identifier] = rep.rep_id

    rep_id_rep_dict = {}

    names = []
    stats_to_put = []
    field_apps_to_save = []
    for stat in ak_stats:
        if stat.field_app_identifier in app_ids_to_query:            
            
            r_id = app_identifier_rep_id_dict[stat.field_app_identifier]
            if not app_identifier_lead_generator_dict[stat.field_app_identifier] == "-1":
                r_id = rep_identifier_rep_id_dict[app_identifier_lead_generator_dict[stat.field_app_identifier]]

            rep = None
            if not r_id in rep_id_rep_dict.keys():
                rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == r_id)
            else:
                rep = rep_id_rep_dict[rep]

            if not stat.field_app_identifier in field_apps_to_save:
                names.append(app_identifier_name_dict[stat.field_app_identifier])
                field_apps_to_save.append(stat.field_app_identifier)
                stat2 = LeaderBoardStat(
                    identifier=Helpers.guid(),
                    dt=start_dt + timedelta(days=3) + timedelta(hours=12),
                    field_app_identifier=stat.field_app_identifier,
                    metric_key="same_week_ab_to_ak",
                    office_identifier=rep.main_office,
                    rep_id=r_id,
                    in_bounds=True,
                    pin_identifier="-1"
                )
                stats_to_put.append(stat2)

    if len(stats_to_put) == 1:
        stats_to_put[0].put()
    elif len(stats_to_put) > 1:
        ndb.put_multi(stats_to_put)

