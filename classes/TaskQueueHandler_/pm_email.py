def pm_email(self):   
    h_p_t = Helpers.pacific_today()
    
    start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
    while not start_dt.isoweekday() == 7:
        start_dt = start_dt + timedelta(days=-1)

    start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

    pms = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.current_status == 0,
            FieldApplicationUser.is_project_manager == True
        )
    )

    pm_identifier_name_dict = {}
    pm_identifier_email_dict = {}
    for pm in pms:        
        pm_identifier_name_dict[pm.identifier] = pm.first_name.strip().title()
        pm_identifier_email_dict[pm.identifier] = pm.rep_email

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
                if not is_pto:                
                    pm_identifier_app_ids_dict[pm].append(pp_sub.field_application_identifier)

    for pm_identifier in pm_identifier_app_ids_dict.keys():
        if len(pm_identifier_app_ids_dict[pm_identifier]) > 0:
            notes = CustomerNote.query(
                ndb.AND(
                    CustomerNote.field_app_identifier.IN(pm_identifier_app_ids_dict[pm_identifier]),
                    CustomerNote.note_key == "cust_comm"
                )
            )

            app_identifiers_found = []
            for note in notes:
                if note.inserted_pacific >= start_dt:
                    app_identifiers_found.append(note.field_app_identifier)

            missing_app_ids = []
            for app_id in pm_identifier_app_ids_dict[pm_identifier]:
                if not app_id in app_identifiers_found:
                    missing_app_ids.append(app_id)

            if len(missing_app_ids) > 0:
                names = []
                msg_body = "Hey " + pm_identifier_name_dict[pm_identifier] + ", "
                for app_id in missing_app_ids:
                    names.append(app_identifier_name_dict[app_id])
                msg_body += "there are customers with whom you have not communicated this week. Please speak with them asap! " + ", ".join(names) + "."
                Helpers.send_email(pm_identifier_email_dict[pm_identifier], "Let's not slip through the cracks", msg_body)
                


