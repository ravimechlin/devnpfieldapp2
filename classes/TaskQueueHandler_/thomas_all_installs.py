def thomas_all_installs(self):
    app_ids_to_query = ["-1"]
    pp_subs = PerfectPacketSubmission.query()
    for pp_sub in pp_subs:
        info = json.loads(pp_sub.extra_info)
        if "project_management_checkoffs" in info.keys():
            if "install" in info["project_management_checkoffs"].keys():
                if "checked" in info["project_management_checkoffs"]["install"].keys():
                    if info["project_management_checkoffs"]["install"]["checked"]:
                        app_ids_to_query.append(pp_sub.field_application_identifier)

    customers = []
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    for app_entry in app_entries:
        customers.append({"first_name": app_entry.customer_first_name.strip().title(), "last_name": app_entry.customer_last_name.strip().title()})

    f = GCSLockedFile("/all_installs.json")
    f.write(json.dumps(customers), "text/plain", "public-read")
    f.unlock()
