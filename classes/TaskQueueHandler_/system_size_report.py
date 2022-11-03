def system_size_report(self):
    import json

    cd_stats = LeaderBoardStat.query(
        LeaderBoardStat.metric_key == "packets_submitted"
    )

    app_ids_to_query = ["-2"]

    for stat in cd_stats:
        app_ids_to_query.append(stat.field_app_identifier)

    packets = PerfectPacketSubmission.query(PerfectPacketSubmission.field_application_identifier.IN(app_ids_to_query))

    app_identifier_install_date_dict = {}

    packet_found_app_ids = []
    for packet in packets:    
        info = json.loads(packet.extra_info)
        if "project_management_checkoffs" in info.keys():
            if "install" in info["project_management_checkoffs"].keys():
                if "checked" in info["project_management_checkoffs"]["install"].keys():
                    if info["project_management_checkoffs"]["install"]["checked"]:
                        if "date" in info["project_management_checkoffs"]["install"].keys():
                            packet_found_app_ids.append(packet.field_application_identifier)
                            app_identifier_install_date_dict[packet.field_application_identifier] = info["project_management_checkoffs"]["install"]["date"]

    app_identifier_name_dict = {}
    app_identifier_postal_dict = {}
    app_identifier_phone_dict = {}
    app_identifier_address_dict = {}
    app_identifier_city_dict = {}
    app_identifier_state_dict = {}
    app_identifier_email_dict = {}
    app_identifier_rep_id_dict = {}
    app_identifier_kwhs_dict = {}
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(packet_found_app_ids))

    rep_ids_to_query = ["-2"]

    for app_entry in app_entries:
        app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
        app_identifier_postal_dict[app_entry.identifier] = app_entry.customer_postal
        app_identifier_phone_dict[app_entry.identifier] = Helpers.format_phone_number(app_entry.customer_phone)
        app_identifier_address_dict[app_entry.identifier] = app_entry.customer_address
        app_identifier_city_dict[app_entry.identifier] = app_entry.customer_city
        app_identifier_state_dict[app_entry.identifier] = app_entry.customer_state
        app_identifier_email_dict[app_entry.identifier] = app_entry.customer_email
        app_identifier_rep_id_dict[app_entry.identifier] = app_entry.rep_id
        app_identifier_kwhs_dict[app_entry.identifier] = str(app_entry.total_kwhs)
        if not app_entry.rep_id in rep_ids_to_query:
            rep_ids_to_query.append(app_entry.rep_id)

    app_identifier_system_size_dict = {}
    proposals = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(packet_found_app_ids))
    for proposal in proposals:
        proposal.fix_system_size()
        deserialized = json.loads(proposal.info)
        app_identifier_system_size_dict[proposal.field_app_identifier] = deserialized["system_size"]

    closers = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))
    rep_id_name_dict = {}
    for closer in closers:
        rep_id_name_dict[closer.rep_id] = closer.first_name.strip().title() + " " + closer.last_name.strip().title()

    data = []
    for app_identifier in app_identifier_name_dict.keys():
        obj = {}
        obj["token"] = app_identifier
        obj["name"] = app_identifier_name_dict[app_identifier]
        obj["install_date"] = app_identifier_install_date_dict[app_identifier]
        obj["address"] = app_identifier_address_dict[app_identifier]
        obj["postal"] = app_identifier_postal_dict[app_identifier]
        obj["city"] = app_identifier_city_dict[app_identifier]
        obj["state"] = app_identifier_state_dict[app_identifier]
        obj["phone"] = app_identifier_phone_dict[app_identifier]
        obj["email"] = app_identifier_email_dict[app_identifier]

        closer_id = app_identifier_rep_id_dict[app_identifier]

        obj["closer"] = rep_id_name_dict[closer_id]
        obj["total_kwhs"] = app_identifier_kwhs_dict[app_identifier]
        obj["system_size"] = app_identifier_system_size_dict[app_identifier]

        data.append(obj)

    f = GCSLockedFile("/InstallsReport/03_26_19_00_00.json")
    f.write(json.dumps(data), "application/json", "public-read")
    f.unlock()
    
    #return