def nightly_lead_assignment_stats(self):
    now = Helpers.pacific_now()
    thirty_days_ago = now + timedelta(days=-30)
    thirty_days_ago = datetime(thirty_days_ago.year, thirty_days_ago.month, thirty_days_ago.day, 0, 0, 0)

    offices = OfficeLocation.query(
        ndb.AND(
            OfficeLocation.active == True,
            OfficeLocation.is_parent == False
        )
    )

    #offices = OfficeLocation.query(OfficeLocation.name == "CA Riverside")

    reps = FieldApplicationUser.query()

    rep_ids = ["-1"]
    rep_identifier_rep_id_dict = {}
    rep_id_rep_identifier_dict = {}
    rep_identifier_name_dict = {}
    rep_identifier_office_identifier_dict = {}
    rep_identifier_accepts_leads_dict = {}
    office_identifier_rep_ids_dict = {}
    for rep in reps:
        rep_ids.append(rep.rep_id)
        rep_identifier_rep_id_dict[rep.identifier] = rep.rep_id
        rep_id_rep_identifier_dict[rep.rep_id] = rep.identifier
        rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
        rep_identifier_office_identifier_dict[rep.identifier] = rep.main_office
        rep_identifier_accepts_leads_dict[rep.identifier] = rep.accepts_leads

        if not rep.main_office in office_identifier_rep_ids_dict.keys():
            office_identifier_rep_ids_dict[rep.main_office] = []
        office_identifier_rep_ids_dict[rep.main_office].append(rep.rep_id)

    rep_identifier_ak_tally_dict = {}    
    rep_identifier_ak_tally_dict2 = {}
    rep_identifier_cd_tally_dict = {}
    rep_identifier_eligible_field_app_ids_count_dict = {}
    rep_identifier_cd_tally_dict2 = {}
    for rep_id in rep_ids:
        if not rep_id == "-1":
            rep_identifier = rep_id_rep_identifier_dict[rep_id]

            rep_identifier_ak_tally_dict[rep_identifier] = 0
            rep_identifier = rep_id_rep_identifier_dict[rep_id]
            rep_identifier_ak_tally_dict2[rep_identifier] = 0
            rep_identifier_cd_tally_dict[rep_identifier] = 0
            rep_identifier_eligible_field_app_ids_count_dict[rep_identifier] = 0 
            rep_identifier_cd_tally_dict2[rep_identifier] = 0

    ab_stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= thirty_days_ago,
            LeaderBoardStat.metric_key == "leads_acquired"
        )
    )

    welfare_ids_to_query = ["-1"]
    welfare_app_ids = []
    for stat in ab_stats:
        welfare_ids_to_query.append(stat.field_app_identifier)

    notes = CustomerNote.query(
        ndb.AND(
            CustomerNote.note_key == "welfare",
            CustomerNote.field_app_identifier.IN(welfare_ids_to_query)
        )
    )

    for note in notes:
        welfare_app_ids.append(note.field_app_identifier)

    field_app_ids_1 = ["-2"]
    for ab_stat in ab_stats:
        field_app_ids_1.append(ab_stat.field_app_identifier)
    

    eligible_field_app_ids_1 = ["-2"]        
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(field_app_ids_1))
    for app_entry in app_entries:
        if app_entry.is_lead and (app_entry.rep_id in rep_ids) and (not app_entry.identifier in welfare_app_ids):
            eligible_field_app_ids_1.append(app_entry.identifier)
            rep_identifier = rep_id_rep_identifier_dict[app_entry.rep_id]
            rep_identifier_eligible_field_app_ids_count_dict[rep_identifier] += 1

    cd_stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.field_app_identifier.IN(eligible_field_app_ids_1),
            LeaderBoardStat.metric_key.IN(["packets_submitted", "packets_submitted_dnq"])
        )
    )

    for stat in cd_stats:
        rep_identifier = rep_id_rep_identifier_dict[stat.rep_id]
        rep_identifier_cd_tally_dict[rep_identifier] += 1

    ak_stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= thirty_days_ago,
            LeaderBoardStat.metric_key == "appointments_kept"
        )
    )

    ak_stats2 = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.field_app_identifier.IN(eligible_field_app_ids_1),
            LeaderBoardStat.metric_key == "appointments_kept"
        )
    )

    for ak_stat in ak_stats2:
        rep_identifier = rep_id_rep_identifier_dict[ak_stat.rep_id]
        if not ak_stat in welfare_app_ids:
            rep_identifier_ak_tally_dict2[rep_identifier] += 1


    field_app_ids_2 = ["-1"]
    for stat in ak_stats:
        if stat.rep_id in rep_ids:
            if not stat.field_app_identifier in welfare_app_ids:
                rep_identifier = rep_id_rep_identifier_dict[stat.rep_id]
                rep_identifier_ak_tally_dict[rep_identifier] += 1
                field_app_ids_2.append(stat.field_app_identifier)

    cd_stats2 = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.field_app_identifier.IN(field_app_ids_2),
            LeaderBoardStat.metric_key.IN(["packets_submitted", "packets_submitted_dnq"])
        )
    )

    for stat in cd_stats2:
        if not stat.field_app_identifier in welfare_app_ids:
            rep_identifier = rep_id_rep_identifier_dict[stat.rep_id]
            rep_identifier_cd_tally_dict2[rep_identifier] += 1

    rep_identifier_conversion_of_leads_to_cds_dict = {}
    for rep_id in rep_ids:
        if not rep_id == "-1":
            rep_identifier = rep_id_rep_identifier_dict[rep_id]
            rep_identifier_conversion_of_leads_to_cds_dict[rep_identifier] = float(0)
            eligible_count = rep_identifier_eligible_field_app_ids_count_dict[rep_identifier]
            if eligible_count > 0:
                cd_count = rep_identifier_cd_tally_dict[rep_identifier]                    
                rep_identifier_conversion_of_leads_to_cds_dict[rep_identifier] = round((float(cd_count) / float(eligible_count)), 2)

    

    rep_identifier_conversion_of_aks_to_cds_dict = {}
    for rep_id in rep_ids:
        if not rep_id == "-1":
            rep_identifier = rep_id_rep_identifier_dict[rep_id]
            rep_identifier_conversion_of_aks_to_cds_dict[rep_identifier] = float(0)
            ak_tally = rep_identifier_ak_tally_dict[rep_identifier]
            if ak_tally > 0:
                cd_tally = rep_identifier_cd_tally_dict2[rep_identifier]
                rep_identifier_conversion_of_aks_to_cds_dict[rep_identifier] = round((float(cd_tally) / float(ak_tally)), 2)

    rep_identifier_conversion_of_ab_to_aks_dict = {}
    for rep_id in rep_ids:
        if not rep_id == "-1":
            rep_identifier = rep_id_rep_identifier_dict[rep_id]
            ab_tally = rep_identifier_eligible_field_app_ids_count_dict[rep_identifier]
            ak_tally = rep_identifier_ak_tally_dict2[rep_identifier]

            if ab_tally > 0:
                rep_identifier_conversion_of_ab_to_aks_dict[rep_identifier] = float(ak_tally) / float(ab_tally)
            else:
                rep_identifier_conversion_of_ab_to_aks_dict[rep_identifier] = 0

    rep_identifier_combined_rate_dict = {}
    for rep_id in rep_ids:
        if not rep_id == "-1":
            rep_identifier = rep_id_rep_identifier_dict[rep_id]
            #metric1 = rep_identifier_conversion_of_leads_to_cds_dict[rep_identifier]
            metric1 = rep_identifier_conversion_of_ab_to_aks_dict[rep_identifier]
            metric2 = rep_identifier_conversion_of_aks_to_cds_dict[rep_identifier]

            the_sum = metric1 + metric2
            the_average = the_sum / float(2)
            the_average = round(the_average, 2)

            rep_identifier_combined_rate_dict[rep_identifier] = the_average

    for office in offices:

        data = []

        

        for rep_id in rep_ids:
            if not rep_id == "-1":
                rep_identifier = rep_id_rep_identifier_dict[rep_id]
                office_identifier = rep_identifier_office_identifier_dict[rep_identifier]
                if office_identifier == office.identifier:
                    accepts_leads = rep_identifier_accepts_leads_dict[rep_identifier]
                    if accepts_leads:
                        obj = {"identifier": rep_identifier}
                        obj["rep_id"] = rep_id
                        obj["name"] = rep_identifier_name_dict[rep_identifier]
                        obj["conversion_of_abs_to_aks"] = rep_identifier_conversion_of_ab_to_aks_dict[rep_identifier]
                        obj["conversion_of_leads_to_cds"] = rep_identifier_conversion_of_leads_to_cds_dict[rep_identifier]
                        obj["conversion_of_aks_to_cds"] = rep_identifier_conversion_of_aks_to_cds_dict[rep_identifier]
                        obj["dual_average"] = rep_identifier_combined_rate_dict[rep_identifier]
                        data.append(obj)

        data = Helpers.bubble_sort(data, "dual_average")
        data.reverse()
        f = GCSLockedFile("/AutoAssignStats/" + office.identifier + ".json")
        #f = GCSLockedFile("/AutoAssignStats/" + office.name.replace(" ", "_") + ".json")
        f.write(json.dumps(data), "text/plain", "public-read")
        f.unlock()
