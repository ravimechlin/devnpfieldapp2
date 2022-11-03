def pm_comm_report(self):
    return
    h_p_t = Helpers.pacific_today()
    
    start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
    while not start_dt.isoweekday() == 7:
        start_dt = start_dt + timedelta(days=-1)

    start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

    start_dt = start_dt + timedelta(days=-7)
    end_dt = end_dt + timedelta(days=-7)

    two_weeks_ago = Helpers.pacific_now() + timedelta(days=-14)

    pms = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.current_status == 0,
            FieldApplicationUser.is_project_manager == True
        )
    )

    pm_identifier_name_dict = {}
    for pm in pms:        
        pm_identifier_name_dict[pm.identifier] = pm.first_name.strip().title()

    app_entries = FieldApplicationEntry.query(
            ndb.AND
            (
                FieldApplicationEntry.deal_closed == True,
                FieldApplicationEntry.archived == False,
                FieldApplicationEntry.save_me == False
            )
        )
    app_ids_to_query = ["-1"]

    app_identifier_name_dict = {}
    for app_entry in app_entries:
        app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
        app_ids_to_query.append(app_entry.identifier)

    app_identifier_commission_review_dict = {}
    pm_identifier_app_ids_dict = {}
    pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.field_application_identifier.IN(app_ids_to_query))
    for pp_sub in pp_subs:
        info = json.loads(pp_sub.extra_info)
        if "project_manager" in info.keys():
            pm = info["project_manager"]
            if pm in pm_identifier_name_dict.keys():
                if not pm in pm_identifier_app_ids_dict.keys():
                    pm_identifier_app_ids_dict[pm] = []
                is_pto = False
                if "project_management_checkoffs" in info.keys():
                    if "received_pto" in info["project_management_checkoffs"].keys():
                        if "checked" in info["project_management_checkoffs"]["received_pto"].keys():
                            if info["project_management_checkoffs"]["received_pto"]["checked"]:
                                is_pto = True

                is_commission_review = True

                if "welcome_call_completed" in info["project_management_checkoffs"].keys():
                    if ("checked" in info["project_management_checkoffs"]["welcome_call_completed"].keys() and info["project_management_checkoffs"]["welcome_call_completed"]["checked"]) or ("date" in info["project_management_checkoffs"]["welcome_call_completed"].keys() and ("1800" in info["project_management_checkoffs"]["welcome_call_completed"]["date"])):
                        if "welcome_email_sent" in info["project_management_checkoffs"].keys():                            
                            if ("checked" in info["project_management_checkoffs"]["welcome_email_sent"].keys() and info["project_management_checkoffs"]["welcome_email_sent"]["checked"]) or ("date" in info["project_management_checkoffs"]["welcome_email_sent"].keys() and ("1800" in info["project_management_checkoffs"]["welcome_email_sent"]["date"])):
                                if "first_payment_received" in info["project_management_checkoffs"].keys():                                    
                                    if ("checked" in info["project_management_checkoffs"]["first_payment_received"].keys() and info["project_management_checkoffs"]["first_payment_received"]["checked"]) or ("date" in info["project_management_checkoffs"]["first_payment_received"].keys() and ("1800" in info["project_management_checkoffs"]["first_payment_received"]["date"])):
                                        if "ntp" in info["project_management_checkoffs"].keys():
                                            if ("checked" in info["project_management_checkoffs"]["ntp"].keys() and info["project_management_checkoffs"]["ntp"]["checked"]) or ("date" in info["project_management_checkoffs"]["ntp"].keys() and ("1800" in info["project_management_checkoffs"]["ntp"]["date"])):
                                                is_commission_review = False

                app_identifier_commission_review_dict[pp_sub.field_application_identifier] = is_commission_review

                if not is_pto:
                    pm_identifier_app_ids_dict[pm].append(pp_sub.field_application_identifier)

    pm_identifier_stats_dict = {}
    for pm_identifier in pm_identifier_app_ids_dict.keys():
        pm_identifier_stats_dict[pm_identifier] = {}
        pm_identifier_stats_dict[pm_identifier]["comm_percentage"] = "100%"
        pm_identifier_stats_dict[pm_identifier]["customers_missed"] = []
        pm_identifier_stats_dict[pm_identifier]["no_response"] = []

    for pm_identifier in pm_identifier_app_ids_dict.keys():        
        if len(pm_identifier_app_ids_dict[pm_identifier]) > 0:
            
            app_identifier_last_comm_dt_dict = {}
            for app_id in pm_identifier_app_ids_dict[pm_identifier]:
                app_identifier_last_comm_dt_dict[app_id] = datetime(1970, 1, 1)            
            
            notes = CustomerNote.query(
                ndb.AND(
                    CustomerNote.field_app_identifier.IN(pm_identifier_app_ids_dict[pm_identifier] + ["-1"]),
                    CustomerNote.note_key == "cust_comm"
                )
            )

            app_ids_found = []
            for note in notes:
                if note.inserted_pacific >= start_dt and note.inserted_pacific <= end_dt:
                    app_ids_found.append(note.field_app_identifier)
                note_date = note.inserted_pacific
                last_date = app_identifier_last_comm_dt_dict[note.field_app_identifier]
                if note_date > last_date:
                    app_identifier_last_comm_dt_dict[note.field_app_identifier] = note_date
                

            missing_app_ids = []
            for app_id in pm_identifier_app_ids_dict[pm_identifier]:
                if not app_id in app_ids_found:
                    missing_app_ids.append(app_id)

            now5 = Helpers.pacific_now()
            for app_id in missing_app_ids:
                name = app_identifier_name_dict[app_id]
                if app_identifier_commission_review_dict[app_id]:
                    last_comm_date = app_identifier_last_comm_dt_dict[app_id]
                    if last_comm_date.year == 1970:
                        name += " (In commission review, Last Communication: Never)"
                    else:
                        delta = now5 - last_comm_date
                        seconds = delta.total_seconds()
                        minutes = seconds / float(60)
                        hours = minutes / float(60)
                        days = hours / float(24)
                        days = int(days)
                        day_text = "days"
                        if days == 1:
                            day_text = "day"
                        name += " (In commission review, Last Communication: " + str(days) + " " + day_text + " ago )"

                pm_identifier_stats_dict[pm_identifier]["customers_missed"].append(name)

            missing_length = len(missing_app_ids)
            total_app_ids = len(pm_identifier_app_ids_dict[pm_identifier])
            pm_identifier_stats_dict[pm_identifier]["comm_percentage"] = float(missing_length) / float(total_app_ids)
            pm_identifier_stats_dict[pm_identifier]["comm_percentage"] *= 100
            pm_identifier_stats_dict[pm_identifier]["comm_percentage"] = float(100) - pm_identifier_stats_dict[pm_identifier]["comm_percentage"]
            pm_identifier_stats_dict[pm_identifier]["comm_percentage"] = round(pm_identifier_stats_dict[pm_identifier]["comm_percentage"], 2)
            pm_identifier_stats_dict[pm_identifier]["comm_percentage"] = int(pm_identifier_stats_dict[pm_identifier]["comm_percentage"])
            pm_identifier_stats_dict[pm_identifier]["comm_percentage"] = str(pm_identifier_stats_dict[pm_identifier]["comm_percentage"])
            pm_identifier_stats_dict[pm_identifier]["comm_percentage"] += "%"

            for app_id in app_identifier_last_comm_dt_dict.keys():
                if app_identifier_last_comm_dt_dict[app_id] < two_weeks_ago:
                    if app_identifier_last_comm_dt_dict[app_id].year == 1970:  
                        pm_identifier_stats_dict[pm_identifier]["no_response"].append(app_identifier_name_dict[app_id] + "(Last Response: NEVER)")
                    else:
                        pm_identifier_stats_dict[pm_identifier]["no_response"].append(app_identifier_name_dict[app_id] + "(Last Response: " + str(app_identifier_last_comm_dt_dict[app_id].month) + "/" + str(app_identifier_last_comm_dt_dict[app_id].day) + ")")

    total_comm_percentage = "100%"
    comm_percentages = []
    for pm_identifier in pm_identifier_app_ids_dict.keys():
        comm_percentages.append(float(pm_identifier_stats_dict[pm_identifier]["comm_percentage"].replace("%", "")))

    if len(comm_percentages) > 0:
        key_length = len(pm_identifier_app_ids_dict.keys())
        comm_sum = 0
        for item in comm_percentages:
            comm_sum += item

        average = float(comm_sum) / float(key_length)
        average = round(average, 2)
        total_comm_percentage = str(average) + "%"

    msg_body = "Total PM Communication: " + str(total_comm_percentage)
    msg_body += "\r\n\r\n\r\n"
    for pm_identifier in pm_identifier_app_ids_dict.keys():
        msg_body += pm_identifier_name_dict[pm_identifier] + " " + str(pm_identifier_stats_dict[pm_identifier]["comm_percentage"])
        msg_body += "\r\n\r\n\r\n"
        msg_body += "Customers Missed:"
        msg_body += "\r\n"
        msg_body += "\r\n".join(pm_identifier_stats_dict[pm_identifier]["customers_missed"])
        msg_body += "\r\n\r\n\r\n"
        msg_body += "Customers with no reponse in last two weeks:"
        msg_body += "\r\n"
        msg_body += "\r\n".join(pm_identifier_stats_dict[pm_identifier]["no_response"])
        msg_body += "\r\n\r\n\r\n"

    notification = Notification.first(Notification.action_name == "PM Comm Report")
    if not notification is None:
        for p in notification.notification_list:
            Helpers.send_email(p.email_address, "Customer Communication Weekly Report", msg_body)




                

            


            
                


