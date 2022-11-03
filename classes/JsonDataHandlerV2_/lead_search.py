def lead_search(self):
    from google.appengine.api import search
    self.response.content_type = "application/json"
    ret_json = {"leads": []}
    index = search.Index(name="cust_names")
    results = index.search(self.request.get("query").replace("(", "").replace(")", ""))

    app_ids_to_query = ["-1"]
    for result in results:
        for field in result.fields:
            if field.name == "cust_identifier":
                app_ids_to_query.append(field.value)

    rep_ids_to_query = ["-1"]
    field_app_identifier_idx_dict = {}
    checklist_keys = ["-1"]
    checklist = Helpers.read_setting("lead_checklist")
    checklist_name_idx_dict = {}
    for item in checklist:
        checklist_name_idx_dict[item] = len(checklist_name_idx_dict.keys())


    digits_str = ""
    for char in self.request.get("query"):
        if char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            digits_str += char

    phone_entries = []
    email_entries = []
    if "@" in self.request.get("query"):
        app_ids_to_query = ["-1"]
        email_entries = FieldApplicationEntry.query(FieldApplicationEntry.customer_email == self.request.get("query").strip())
    elif len(digits_str) == 10:
        phone_entries = FieldApplicationEntry.query(FieldApplicationEntry.customer_phone == digits_str)
    else:
        email_entries = []

    for entry in email_entries:
        app_ids_to_query.append(entry.identifier)
    for entry in phone_entries:
        app_ids_to_query.append(entry.identifier)



    app_ids_to_query2 = ["-1"]
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    for app_entry in app_entries:
        if app_entry.processed == 1:
            app_ids_to_query2.append(app_entry.identifier)
            if not app_entry.lead_generator in rep_ids_to_query:
                rep_ids_to_query.append(app_entry.lead_generator)

            checklist_keys.append("lead_checklist_for_" + app_entry.identifier)

            field_app_identifier_idx_dict[app_entry.identifier] = len(ret_json["leads"])            

            obj = {}
            obj["name"] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
            obj["identifier"] = app_entry.identifier
            obj["location"] = app_entry.customer_city + ", " + app_entry.customer_state
            obj["address"] = app_entry.customer_address + "\n" + app_entry.customer_city + ", " + app_entry.customer_state + "\n" + app_entry.customer_postal
            obj["phone"] = Helpers.format_phone_number(app_entry.customer_phone)
            obj["email"] = app_entry.customer_email
            obj["solar_pro"] = app_entry.lead_generator
            obj["solar_pro_identifier"] = app_entry.lead_generator
            obj["sp_two_time"] = str(app_entry.sp_two_time).split(".")[0]
            obj["rep_notes"] = ""
            obj["admin_notes"] = ""
            obj["admin_checklist"] = []

            for item in checklist:
                obj["admin_checklist"].append({"name": item, "checked": False, "date": "1970-01-01"})
            ret_json["leads"].append(obj)

    notes = CustomerNote.query(
            ndb.AND(
                CustomerNote.note_key.IN(["rep_lead_notes", "admin_lead_notes"]),
                CustomerNote.field_app_identifier.IN(app_ids_to_query2)
            )
        )

    for note in notes:
        idx = field_app_identifier_idx_dict[note.field_app_identifier]
        note_key_property_dict = {"rep_lead_notes": "rep_notes", "admin_lead_notes": "admin_notes"}
        ret_json["leads"][idx][note_key_property_dict[note.note_key]] = json.loads(note.content)["txt"][0]

    checklist_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(checklist_keys))
    for checklist_kv in checklist_kvs:
        identifier = checklist_kv.keyy.split("_")[3]
        idx = field_app_identifier_idx_dict[identifier]
        value = json.loads(checklist_kv.val)
        for item in value.keys():
            cnt = 0
            for item2 in ret_json["leads"][idx]["admin_checklist"]:
                if item2["name"] == item:
                    ret_json["leads"][idx]["admin_checklist"][checklist_name_idx_dict[item2["name"]]] = value[item]
                cnt += 1

    rep_identifier_name_dict = {}
    reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
    for rep in reps:
        rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

    for l in ret_json["leads"]:
        try:
            l["solar_pro"] = rep_identifier_name_dict[l["solar_pro_identifier"]]
        except:
            l["solar_pro"] = "n/a"

    rep_ids_to_query2 = ["-1"]

    leads = Lead.query(Lead.field_app_identifier.IN(app_ids_to_query2))
    bad_idxs = []
    for lead in leads:
        if lead.field_app_identifier in field_app_identifier_idx_dict.keys():
            idx = field_app_identifier_idx_dict[lead.field_app_identifier]
            try:
                ret_json["leads"][idx]["status"] = lead.status
                ret_json["leads"][idx]["claimed_dt"] = str(lead.dt_accepted).split(".")[0]
                ret_json["leads"][idx]["assigned_dt"] = str(lead.dt_created).split(".")[0]
                ret_json["leads"][idx]["rep_identifier"] = lead.rep_identifier
            except:
                bad_idxs.append(idx)

            if not lead.rep_identifier in rep_ids_to_query2:
                rep_ids_to_query2.append(lead.rep_identifier)

    cnt = 0
    new_data = []
    for lead in ret_json["leads"]:
        if not cnt in bad_idxs:
            new_data.append(lead)
        cnt += 1
    ret_json["leads"] = new_data

    rep_identifier_name_dict2 = {}
    reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query2))
    for rep in reps:
        rep_identifier_name_dict2[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

    new_data = []
    for l in ret_json["leads"]:
        if "rep_identifier" in l.keys():
            new_data.append(l)

    ret_json["leads"] = new_data

    for l in ret_json["leads"]:
        rep_identifier = l["rep_identifier"]
        l["rep_name"] = rep_identifier_name_dict2[rep_identifier]

    self.response.out.write(json.dumps(ret_json))
