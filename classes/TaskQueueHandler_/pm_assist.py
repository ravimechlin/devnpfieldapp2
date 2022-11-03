def pm_assist(self):
    from datetime import date
    from datetime import timedelta
    from datetime import datetime
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
        app_ids_to_query.append(app_entry.identifier)
        app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()

    done = False
    jaysawn = {}
    pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.field_application_identifier.IN(app_ids_to_query))
    for pp_sub in pp_subs:
        if done:
            continue
        info = json.loads(pp_sub.extra_info)
        if "project_manager" in info.keys():
            if isinstance(info["project_manager"], str) or isinstance(info["project_manager"], unicode):
                if info["project_manager"] == self.request.get("user"):
                    skip = False
                    if "project_management_checkoffs" in info.keys():
                        if "received_pto" in info["project_management_checkoffs"].keys():
                            if info["project_management_checkoffs"]["received_pto"]["checked"] == True:
                                skip = True
                    if not skip:                        
                        if "project_management_checkoffs" in info.keys():
                            if "install" in info["project_management_checkoffs"].keys():
                                if "date" in info["project_management_checkoffs"]["install"].keys():
                                    today = Helpers.pacific_today()
                                    dt_vals = info["project_management_checkoffs"]["install"]["date"].split("-")
                                    dt = date(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                                    if dt < today:
                                        checked = False
                                        if "checked" in info["project_management_checkoffs"]["install"].keys():
                                            checked = info["project_management_checkoffs"]["install"]["checked"]

                                        if not checked:
                                            done = True
                                            jaysawn = {"type": "install_passed", "identifier": pp_sub.field_application_identifier, "date": info["project_management_checkoffs"]["install"]["date"], "name": app_identifier_name_dict[pp_sub.field_application_identifier]}
                                            f = GCSLockedFile("/Temp/pm_assist_" + self.request.get("token") + ".json")
                                            f.write(json.dumps(jaysawn), "text/plain", "public-read")
                                            f.unlock()
                        
                        if "project_management_checkoffs" in info.keys():
                            if "install" in info["project_management_checkoffs"].keys():
                                if "date" in info["project_management_checkoffs"]["install"].keys():
                                    dt_vals = info["project_management_checkoffs"]["install"]["date"].split("-")
                                    dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                                    now = Helpers.pacific_now()

                                    if (now - dt).total_seconds() >= float(60 * 60 * 24 * 14):
                                        has_pto = False
                                        if "received_pto" in info["project_management_checkoffs"].keys():
                                            if "checked" in info["project_management_checkoffs"]["received_pto"].keys():
                                                has_pto = info["project_management_checkoffs"]["received_pto"]["checked"]

                                        if not has_pto:
                                            kv2 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pto_intervention_" + pp_sub.field_application_identifier)
                                            if kv2 is None:
                                                done = True
                                                jaysawn = {"type": "pto_intervention", "identifier": pp_sub.field_application_identifier, "date": info["project_management_checkoffs"]["install"]["date"], "name": app_identifier_name_dict[pp_sub.field_application_identifier]}
                                                f = GCSLockedFile("/Temp/pm_assist_" + self.request.get("token") + ".json")
                                                f.write(json.dumps(jaysawn), "text/plain", "public-read")
                                                f.unlock()

            else:
                x = 5
                #Helpers.send_email("rnirnber@gmail.com", "result", str(type(info["project_manager"])))
                                            
    kv = KeyValueStoreItem(
        identifier=Helpers.guid(),
        keyy="pm_assist_status_" + self.request.get("token"),
        val="1",
        expiration=Helpers.pacific_now() + timedelta(days=1)
    )
    kv.put()

