def sales_stats_report(self):
    from datetime import datetime
    import tablib
    
    start_dt_vals = self.request.get("start_dt").split("-")
    end_dt_vals = self.request.get("end_dt").split("-")
    start = datetime(int(start_dt_vals[0]), int(start_dt_vals[1]), int(start_dt_vals[2]))
    end = datetime(int(end_dt_vals[0]), int(end_dt_vals[1]), int(end_dt_vals[2]), 23, 59, 59)

    metric_keys = ["hours_knocked_v2", "leads_acquired", "packets_submitted", "appointments_kept"]

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= start,
            LeaderBoardStat.dt <= end,
            LeaderBoardStat.metric_key.IN(metric_keys)
        )
    )

    stats_cpy = []
    rep_ids_to_query = ["-1"]
    for stat in stats:
        stats_cpy.append(stat)
        rep_ids_to_query.append(stat.rep_id)

    rep_id_rep_name_dict = {}
    rep_id_rep_office_dict = {}
    rep_id_user_type_dict = {}
    office_ids_to_query = ["-1"]
    reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))
    for rep in reps:
        rep_id_rep_name_dict[rep.rep_id] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
        rep_id_rep_office_dict[rep.rep_id] = rep.main_office
        if not rep.main_office in office_ids_to_query:
            office_ids_to_query.append(rep.main_office)
        rep_id_user_type_dict[rep.rep_id] = rep.user_type

    office_identifier_name_dict = {}
    offices = OfficeLocation.query(OfficeLocation.identifier.IN(office_ids_to_query))
    for office in offices:
        office_identifier_name_dict[office.identifier] = office.name

    rep_id_hk_tally = {}
    rep_id_ab_tally = {}
    rep_id_ak_tally = {}
    rep_id_cd_tally = {}

    
    for rep_id in rep_id_rep_office_dict.keys():
        for office_identifier in office_identifier_name_dict.keys():
            if rep_id_rep_office_dict[rep_id] == office_identifier:
                rep_id_rep_office_dict[rep_id] = office_identifier_name_dict[office_identifier]

    for rep_id in rep_id_rep_name_dict.keys():
        rep_id_hk_tally[rep_id] = 0
        rep_id_ab_tally[rep_id] = 0
        rep_id_ak_tally[rep_id] = 0
        rep_id_cd_tally[rep_id] = 0

    cd_app_ids = ["-1"]
    for stat in stats_cpy:
        rep_id = stat.rep_id
        rep_id_hk_tally[rep_id] += int(stat.metric_key == "hours_knocked_v2")
        rep_id_ab_tally[rep_id] += int(stat.metric_key == "leads_acquired")
        rep_id_ak_tally[rep_id] += int(stat.metric_key == "appointments_kept")
        rep_id_cd_tally[rep_id] += int(stat.metric_key == "packets_submitted")
        if stat.metric_key == "packets_submitted":
            if not stat.field_app_identifier in cd_app_ids:
                cd_app_ids.append(stat.field_app_identifier)

    app_entries2 = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(cd_app_ids))
    app_identifier_lead_generator_dict = {}

    solar_pro_ids_to_query = ["-1"]
    for app_entry in app_entries2:
        if not app_entry.lead_generator == "-1":
            solar_pro_ids_to_query.append(app_entry.lead_generator)
            app_identifier_lead_generator_dict[app_entry.identifier] = app_entry.lead_generator

    solar_pro_identifier_rep_id_dict = {}
    solar_pros = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(solar_pro_ids_to_query))
    for solar_pro in solar_pros:
        solar_pro_identifier_rep_id_dict[solar_pro.identifier] = solar_pro.rep_id

    for stat in stats_cpy:
        if stat.metric_key == "packets_submitted":
            if stat.field_app_identifier in app_identifier_lead_generator_dict.keys():
                lead_generator = app_identifier_lead_generator_dict[stat.field_app_identifier]
                solar_pro_rep_id = solar_pro_identifier_rep_id_dict[lead_generator]
                try:
                    rep_id_cd_tally[solar_pro_rep_id] += 1
                except:
                    x5 = 5
        

    

    headers = ('Rep Name', 'Rep Office', 'HK V2', 'AB', 'AK', 'CD')
    data = []
    for rep_id in rep_id_hk_tally.keys():
        #ak_text = "n/a"
        ak_text = str(rep_id_ak_tally[rep_id])            
        cd_text = str(rep_id_cd_tally[rep_id])

        data.append(
            (rep_id_rep_name_dict[rep_id],
            rep_id_rep_office_dict[rep_id],
            str(rep_id_hk_tally[rep_id]),
            str(rep_id_ab_tally[rep_id]),
            ak_text,
            cd_text)
        )

    structured_data = tablib.Dataset(*data, headers=headers)
    attachment_data = {}
    attachment_data["data"] = [base64.b64encode(structured_data.csv)]
    attachment_data["content_types"] = ["text/csv"]
    attachment_data["filenames"] = ["Sales Stats Report: " + self.request.get("start_dt") + " --- " + self.request.get("end_dt") + ".csv"]

    Helpers.send_email(self.request.get("email"), "Your Sales Stats Report", "See attached....", attachment_data)

