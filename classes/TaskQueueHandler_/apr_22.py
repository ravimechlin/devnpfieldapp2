def apr_22(self):
    rep_identifiers = ["38ea235e774da99d0ff8d1c6d943329dc2152f8d8a3a6fcae3c5179912dd665f7c6fe55d42bf3e7127704335165a964c5ad800b4b0569506c3631c430dbcc1f7", "fff4eb8e26f78c8fc8ec1ca092dc94061f9b470e058cf91a3e0db3d902accb45c17b8744669a6ab2ce20e6bd9d0ea591ef2b6fbcf64c19bb0d02c86fba8da828", "67b5798c152f57e06bab08b6a4fe42f74cff8eda4d2db44f96e775fcc78d3a724002c98f1d7ff4cce21b9fdba6d01eb37b7955950e2470919c4993e3f094cadb", "e9a96b14200f1d345e6dd5c5837506522f65b77e7bee41acf19d51bd9a474be2c008022a687e0268a169d6be70237081d91af9d46195df350ebe67018fb86596", "41738e1361421e6441dae232a634c3b700b4f660b37daa2710af2d26c12e21fa7fe98010153f66d4a1d04c0fd444752ffe93f16122d29fd0318e98ed0ddd968c", "9e898c0d25421332ff79c31feee116a2a02995015a6d68075be87b58d60aa2b82cb8a2d47df39dd6ec0de31a97dee839344f3ef4ee20ec7a80be4d6f7fa4e279"]
    rep_identifier_name_dict = {}
    reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_identifiers))
    for rep in reps:
        rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

    packets = PerfectPacketSubmission.query(PerfectPacketSubmission.rep_identifier.IN(rep_identifiers))
    app_ids_to_query = ["-1"]
    app_identifier_idx_dict = {}
    data = []
    for packet in packets:
        info = json.loads(packet.extra_info)
        if "project_management_checkoffs" in info.keys():
                if "install" in info["project_management_checkoffs"].keys():
                    if "checked" in info["project_management_checkoffs"]["install"].keys():
                        if info["project_management_checkoffs"]["install"]["checked"]:
                            if "date" in info["project_management_checkoffs"]["install"].keys():
                                app_ids_to_query.append(packet.field_application_identifier)
                                app_identifier_idx_dict[packet.field_application_identifier] = len(data)
                                obj = {}
                                obj["field_app_identifier"] = packet.field_application_identifier
                                obj["install_date"] = info["project_management_checkoffs"]["install"]["date"]
                                obj["rep_name"] = rep_identifier_name_dict[packet.rep_identifier]
                                obj["keep"] = True
                                data.append(obj)

    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    app_identifier_office_dict = {}
    office_ids_to_query = []
    for app_entry in app_entries:
        idx = app_identifier_idx_dict[app_entry.identifier]
        data[idx]["total_kwhs"] = str(app_entry.total_kwhs)
        data[idx]["first_name"] = app_entry.customer_first_name
        data[idx]["last_name"] = app_entry.customer_last_name
        data[idx]["address"] = app_entry.customer_address
        data[idx]["city"] = app_entry.customer_city
        data[idx]["state"] = app_entry.customer_state
        data[idx]["postal"] = app_entry.customer_postal
        data[idx]["phone"] = Helpers.format_phone_number(app_entry.customer_phone)
        data[idx]["utility_provider"] = app_entry.utility_provider
        data[idx]["app_entry"] = app_entry
        data[idx]["office_identifier"] = app_entry.office_identifier
        data[idx]["fund"] = "Unavailable"
        data[idx]["panel_quantity"] = "Unavailable"
        data[idx]["photo"] = "Not Available"

        if Helpers.gcs_file_exists("/InstallPhotos/" + app_entry.identifier + ".jpg"):
            data[idx]["photo"] = "https://storage.googleapis.com/npfieldapp.appspot.com/InstallPhotos/" + app_entry.identifier + ".jpg"
        elif Helpers.gcs_file_exists("/InstallPhotos/" + app_entry.identifier + ".png"):
            data[idx]["photo"] = "https://storage.googleapis.com/npfieldapp.appspot.com/InstallPhotos/" + app_entry.identifier + ".png"

        app_identifier_office_dict[app_entry.identifier] = app_entry.office_identifier
        if not app_entry.office_identifier in office_ids_to_query:
            office_ids_to_query.append(app_entry.office_identifier)

    office_identifier_market_dict = {}
    offices = OfficeLocation.query(OfficeLocation.identifier.IN(office_ids_to_query))
    for office in offices:
        office_identifier_market_dict[office.identifier] = office.parent_identifier

    bookings = SurveyBooking.query(SurveyBooking.field_app_identifier.IN(app_ids_to_query))
    for booking in bookings:
        idx = app_identifier_idx_dict[booking.field_app_identifier]
        data[idx]["fund"] = booking.fund
        data[idx]["booking"] = booking

    proposals = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(app_ids_to_query))
    for proposal in proposals:
        idx = app_identifier_idx_dict[proposal.field_app_identifier]
        proposal.fix_additional_amount()
        proposal.fix_system_size()
        proposal_dict = json.loads(proposal.info)
        panel_qty = proposal_dict["panel_qty"]
        if "new_panel_qty" in proposal_dict.keys():
            panel_qty = proposal_dict["new_panel_qty"]
        data[idx]["panel_quantity"] = panel_qty
        data[idx]["proposal"] = proposal_dict

    pricing_structures = Helpers.get_pricing_structures()
    funds = Helpers.list_funds()
    for obj in data:
        
        office_identifier = app_identifier_office_dict[obj["field_app_identifier"]]
        market_key = office_identifier_market_dict[office_identifier]

        if "proposal" in obj.keys():
            p = obj["proposal"]

            s_cost = round(float(Helpers.crunch("fx_Total_System_Cost", market_key, obj["app_entry"], obj["booking"], p, pricing_structures, funds)), 2)
            obj["system_cost"] = str(s_cost)
        else:
            obj["system_cost"] = "Unavailable"        

    for obj in data:
        try:
            if "proposal" in obj.keys():
                del obj["proposal"]
            if "app_entry" in obj.keys():
                del obj["app_entry"]
            if "booking" in obj.keys():
                del obj["booking"]
        except:
            x = 5

    f = GCSLockedFile("/Apr22/data.json")
    f.write(json.dumps(data), "text/plain", "public-read")
    f.unlock()

