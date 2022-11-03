def breadcrumbs_report(self):
    from datetime import datetime
    import tablib

    start_dt_vals = self.request.get("start_dt").split("-")
    end_dt_vals = self.request.get("end_dt").split("-")
    mode = self.request.get("mode")
    recipient = str(self.request.get("recipient"))
    rep_identifier = str(self.request.get("rep_identifier"))
    
    start_dt = datetime(int(start_dt_vals[0]), int(start_dt_vals[1]), int(start_dt_vals[2]))
    end_dt = datetime(int(end_dt_vals[0]), int(end_dt_vals[1]), int(end_dt_vals[2]), 23, 59, 59)

    breadcrumbs = []

    eligible_metric_keys = ["app_stat_R", "packets_submitted", "app_stat_CB", "app_stat_NQ", "app_stat_NI", "full_ab", "partial_ab", "leads_acquired"]

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= start_dt,
            LeaderBoardStat.dt <= end_dt,
            LeaderBoardStat.metric_key.IN(eligible_metric_keys)
        )
    )
    plain_text = ""

    rep_identifier_name_dict = {}
    reps = FieldApplicationUser.query(FieldApplicationUser.user_type.IN(["field", "asst_mgr", "co_mgr", "sales_dist_mgr", "rg_mgr", "solar_pro", "solar_pro_manager", "energy_expert", "sales_manager"]))
    for rep in reps:
        rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

    if mode == "individual":
        rep = FieldApplicationUser.first(FieldApplicationUser.identifier == rep_identifier)
        if not rep is None: 
            rep_id = rep.rep_id

            crumbs = UserLocationLogItem.query(
                ndb.AND(
                    UserLocationLogItem.rep_identifier == rep.identifier,
                    UserLocationLogItem.created >= start_dt,
                    UserLocationLogItem.created <= end_dt
                )
            )

            for crumb in crumbs:
                if crumb.pin_latitude > -300:
                    breadcrumbs.append(crumb)

            r_tally = 0
            cd_tally = 0
            cb_tally = 0
            nq_tally = 0
            ni_tally = 0
            full_ab_tally = 0
            partial_ab_tally = 0
            ab_tally = 0
            qc_total = 0
            out_of_bounds_qc_total = 0
            net_qcs = 0
            for stat in stats:
                if stat.rep_id == rep_id:
                    r_tally += int(stat.metric_key == "app_stat_R")
                    cd_tally += int(stat.metric_key == "packets_submitted")
                    cb_tally += int(stat.metric_key == "app_stat_CB")
                    nq_tally += int(stat.metric_key == "app_stat_NQ")
                    ni_tally += int(stat.metric_key == "app_stat_NI")
                    full_ab_tally += (int(stat.metric_key == "full_ab"))
                    partial_ab_tally += int(stat.metric_key == "partial_ab")
                    ab_tally += (int(stat.metric_key == "leads_acquired"))

                    if stat.in_bounds == False:
                        if stat.metric_key == "app_stat_NI":
                            out_of_bounds_qc_total += 1

            qc_total = ab_tally + ni_tally
            net_qcs = qc_total - out_of_bounds_qc_total
            if net_qcs < 0:
                net_qcs = 0

            plain_text += "Rep: " + rep.first_name.strip().title() + " " + rep.last_name.strip().title() + "\r\n"
            plain_text += "Dates: " + start_dt.strftime("%m/%d/%Y") + "  ---  " + end_dt.strftime("%m/%d/%Y") + "\r\n"
            plain_text += "\r\n"
            plain_text += "R - " + str(r_tally) + "\r\n"
            plain_text += "CD - " + str(cd_tally) + "\r\n"
            plain_text += "CB - " + str(cb_tally) + "\r\n"
            plain_text += "NQ - " + str(nq_tally) + "\r\n"
            plain_text += "NI - " + str(ni_tally) + "\r\n"
            plain_text += "Full AB - " + str(full_ab_tally) + "\r\n"
            plain_text += "Partial AB - " + str(partial_ab_tally) + "\r\n"
            plain_text += "\r\n"
            plain_text += "Total qualified contacts (QCs): " + str(qc_total) + "\r\n"
            plain_text += "Out of bounds QCs: " + str(out_of_bounds_qc_total) + "\r\n"
            plain_text += "Net QCs: " + str(net_qcs)

    elif mode == "everyone":
        crumbs = UserLocationLogItem.query(
            ndb.AND(
                UserLocationLogItem.created >= start_dt,
                UserLocationLogItem.created <= end_dt
            )
        )

        for crumb in crumbs:
            if crumb.pin_latitude > -300:
                breadcrumbs.append(crumb)
        
        rep_identifier_tallies_dict = {}
        rep_identifier_rep_id_dict = {}
        rep_id_rep_identifier_dict = {}
        
        blank_tally = {"out_of_bounds": 0, "ab_tally": 0, "full_ab_tally": 0, "ni_tally": 0}
        
        for rep in reps:            
            rep_identifier_tallies_dict[rep.identifier] = json.loads(json.dumps(blank_tally))
            rep_identifier_rep_id_dict[rep.identifier] = rep.rep_id
            rep_id_rep_identifier_dict[rep.rep_id] = rep.identifier

        for stat in stats:
            r_id = stat.rep_id
            rep_identifierr = rep_id_rep_identifier_dict[r_id]
            tally_dict = rep_identifier_tallies_dict[rep_identifierr]
            tally_dict["full_ab_tally"] += int(stat.metric_key == "full_ab")
            tally_dict["ab_tally"] += int(stat.metric_key == "leads_acquired")

            if stat.in_bounds == False:
                if stat.metric_key == "app_stat_NI":
                    tally_dict["out_of_bounds"] += 1

        plain_text += "Dates: " + start_dt.strftime("%m/%d/%Y") + "  ---  " + end_dt.strftime("%m/%d/%Y") + "\r\n"
        plain_text += "Net QCs / Full ABs" + "\r\n"
        plain_text += "\r\n\r\n"

        keys = rep_identifier_tallies_dict.keys()
        for key in keys:
            tally_dict = rep_identifier_tallies_dict[key]
            tally_dict["net_qcs"] = (tally_dict["ab_tally"] + tally_dict["ni_tally"]) - tally_dict["out_of_bounds"]
            plain_text += "----------------------------------------" + "\r\n"
            plain_text += rep_identifier_name_dict[key] + ": " + str(tally_dict["net_qcs"]) + " / " + str(tally_dict["full_ab_tally"]) + "\r\n"
            plain_text += "----------------------------------------" + "\r\n\r\n"




        

    token = Helpers.guid()
    f = GCSLockedFile("/TempDocs/" + token + ".txt")
    f.write(plain_text, "text/plain", "public-read")

    breadcrumb_items = []
    for crumb in breadcrumbs:
        breadcrumb_items.append({"name": rep_identifier_name_dict[crumb.rep_identifier], "in_bounds": str(crumb.in_bounds).lower(), "timestamp": str(crumb.created).split(".")[0]})
    breadcrumb_items = Helpers.bubble_sort(breadcrumb_items, "timestamp")
    headers = ('Rep', 'In Bounds', 'Timestamp')
    csv_data = []
    for crumb in breadcrumb_items:
        csv_data.append((crumb["name"],
            crumb["in_bounds"],
            crumb["timestamp"]))

    structured_data = tablib.Dataset(*csv_data, headers=headers)
    token2 = Helpers.guid()
    f2 = GCSLockedFile("/TempDocs/" + token2 + ".csv")
    f2.write(structured_data.csv, "text/csv", "public-read")


    from google.appengine.api import app_identity
    attachment_data = {}
    attachment_data["data"] = ["https://storage.googleapis.com/" + app_identity.get_application_id() + ".appspot.com/TempDocs/" + token + ".txt", "https://storage.googleapis.com/" + app_identity.get_application_id() + ".appspot.com/TempDocs/" + token2 + ".csv"]
    attachment_data["content_types"] = ["text/plain", "text/csv"]
    attachment_data["filenames"] = ["report_" + mode + "_" + start_dt.strftime("%Y_%m_%d") + "__" + end_dt.strftime("%Y_%m_%d") + ".txt", "breadcrumb_timestamps_" + start_dt.strftime("%Y_%m_%d") + "__" + end_dt.strftime("%Y_%m_%d") + ".csv"]

    Helpers.send_email(recipient, "The Report You Requested", "Attached...", attachment_data)
