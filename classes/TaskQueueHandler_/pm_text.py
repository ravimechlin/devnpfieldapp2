def pm_text(self):
    now = Helpers.pacific_now()
    if now.isoweekday() in [6, 7]:
        return
    
    pms = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.current_status == 0,
            FieldApplicationUser.is_project_manager == True
        )
    )

    pm_identifier_name_dict = {}
    pm_identifier_phone_dict = {}
    for pm in pms:        
        pm_identifier_name_dict[pm.identifier] = pm.first_name.strip().title()
        pm_identifier_phone_dict[pm.identifier] = pm.rep_phone

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
                welcome_call_completed = False

                if "project_management_checkoffs" in info.keys():
                    if "received_pto" in info["project_management_checkoffs"].keys():
                        if "checked" in info["project_management_checkoffs"]["received_pto"].keys():
                            if info["project_management_checkoffs"]["received_pto"]["checked"]:
                                is_pto = True
                if "project_management_checkoffs" in info.keys():
                    if "welcome_call_completed" in info["project_management_checkoffs"].keys():
                        if "checked" in info["project_management_checkoffs"]["welcome_call_completed"].keys():
                            if info["project_management_checkoffs"]["welcome_call_completed"]["checked"]:
                                welcome_call_completed = True
                
                if (not is_pto) and (welcome_call_completed):                
                    pm_identifier_app_ids_dict[pm].append(pp_sub.field_application_identifier)

    two_weeks_ago = Helpers.pacific_now() + timedelta(days=-14)

    for pm_identifier in pm_identifier_app_ids_dict.keys():
        if len(pm_identifier_app_ids_dict[pm_identifier]) > 0:
            notes = CustomerNote.query(
                ndb.AND(
                    CustomerNote.field_app_identifier.IN(pm_identifier_app_ids_dict[pm_identifier]),
                    CustomerNote.note_key == "cust_comm"
                )
            )

            note_keys_to_query = ["-2"]
            note_identifier_field_app_id_dict = {}
            note_identifier_dt_dict = {}
            for note in notes:                
                note_keys_to_query.append("cust_response_to_note_" + note.identifier)
                note_identifier_field_app_id_dict[note.identifier] = note.field_app_identifier
                note_identifier_dt_dict[note.identifier] = note.inserted_pacific


            field_app_identifier_last_comm_dt_dict = {}
            for app_id in pm_identifier_app_ids_dict[pm_identifier]:
                field_app_identifier_last_comm_dt_dict[app_id] = datetime(1970, 1, 1)

            kv_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(note_keys_to_query))
            for kv in kv_items:                
                if kv.val == "1":
                    note_id = kv.keyy.replace("cust_response_to_note_", "")
                    app_id = note_identifier_field_app_id_dict[note_id]
                    last_dt = field_app_identifier_last_comm_dt_dict[app_id]
                    note_dt = note_identifier_dt_dict[note_id]
                    if note_dt > last_dt:
                        field_app_identifier_last_comm_dt_dict[app_id] = note_dt

            debug_dict = {}
            for key in field_app_identifier_last_comm_dt_dict.keys():
                debug_dict[key] = str(field_app_identifier_last_comm_dt_dict[key])

            missing_app_ids = []
            for app_id in field_app_identifier_last_comm_dt_dict.keys():
                if field_app_identifier_last_comm_dt_dict[app_id] < two_weeks_ago:
                    missing_app_ids.append(app_id)

            if len(missing_app_ids) > 0:
                names = []
                msg_body = "Hey " + pm_identifier_name_dict[pm_identifier] + ", "
                for app_id in missing_app_ids:
                    names.append(app_identifier_name_dict[app_id])
                msg_body += " the following customers have not responded to you in the last 2 weeks.  Please speak with them asap! " + ", ".join(names) + "."
                Helpers.send_sms(pm_identifier_phone_dict[pm_identifier], msg_body)


