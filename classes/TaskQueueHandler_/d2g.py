def d2g(self):
    fn = self.request.get("fn")

    if fn == "closed_deals":
        start_dt_vals = self.request.get("start_dt").split("-")
        start_dt = datetime(int(start_dt_vals[0]), int(start_dt_vals[1]), int(start_dt_vals[2]))
        
        end_dt_vals = self.request.get("end_dt").split("-")
        end_dt = datetime(int(end_dt_vals[0]), int(end_dt_vals[1]), int(end_dt_vals[2]), 23, 59, 59)

        pp_subs = PerfectPacketSubmission.query(
            ndb.AND(
               PerfectPacketSubmission.rep_submission_date >= start_dt,
               PerfectPacketSubmission.rep_submission_date <= end_dt
           )
        )

        app_identifier_pp_sub_dict = {}
        app_identifier_cd_date_dict = {}
        app_ids_to_query = ["-1"]
        for pp_sub in pp_subs:
            info = json.loads(pp_sub.extra_info)
            is_pto = False
            if "project_management_checkoffs" in info.keys():
                if "received_pto" in info["project_management_checkoffs"].keys():
                    if "checked" in info["project_management_checkoffs"]["received_pto"].keys():
                        if info["project_management_checkoffs"]["received_pto"]["checked"]:
                            is_pto = True


            if not pp_sub.save_me:
                if (is_pto) or ((not is_pto) and (not pp_sub.archived)):
                    app_identifier_pp_sub_dict[pp_sub.field_application_identifier] = pp_sub
                    app_ids_to_query.append(pp_sub.field_application_identifier)
                    app_identifier_cd_date_dict[pp_sub.field_application_identifier] = str(pp_sub.rep_submission_date.date())

        csv_rows = []
        app_identifier_app_entry_dict = {}
        app_identifier_idx_dict = {}
        solar_pro_ids_to_query = ["-1"]
        logger_kvs_to_query = ["-1"]
        sys_cost_kvs_to_query = ["-1"]
        rep_ids_to_query = ["-1"]
        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        office_ids_to_query = ["-1"]
        app_identifier_office_identifier_dict = {}
        for app_entry in app_entries:
            app_identifier_app_entry_dict[app_entry.identifier] = app_entry
            app_identifier_idx_dict[app_entry.identifier] = len(csv_rows)
            obj = {} 
            obj["identifier"] = app_entry.identifier
            obj["name"] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
            obj["address"] = app_entry.customer_address + "\n" + app_entry.customer_city + ", " + app_entry.customer_state + "\n" + app_entry.customer_postal
            obj["solar_pro"] = app_entry.lead_generator
            obj["rep"] = app_entry.rep_id
            obj["email"] = app_entry.customer_email
            obj["phone"] = Helpers.format_phone_number(app_entry.customer_phone)
            obj["last_year_kwh_usage"] = str(round(float(app_entry.total_kwhs), 2))
            obj["sp2"] = str(app_entry.sp_two_time)
            obj["logger_deployed"] = "False"
            if not app_entry.lead_generator in solar_pro_ids_to_query:
                solar_pro_ids_to_query.append(app_entry.lead_generator)
            if not app_entry.rep_id in rep_ids_to_query:
                rep_ids_to_query.append(app_entry.rep_id)

            if not app_entry.office_identifier in office_ids_to_query:
                office_ids_to_query.append(app_entry.office_identifier)
            app_identifier_office_identifier_dict[app_entry.identifier] = app_entry.office_identifier

            logger_kvs_to_query.append(app_entry.identifier + "_data_logging")
            sys_cost_kvs_to_query.append("total_system_cost_" + app_entry.identifier)
            csv_rows.append(obj)

        
        office_locations = OfficeLocation.query(OfficeLocation.identifier.IN(office_ids_to_query))
        office_identifier_market_identifier_dict = {}
        for office in office_locations:
            office_identifier_market_identifier_dict[office.identifier] = office.parent_identifier

        solar_pro_identifier_name_dict = {"-1": "n/a"}
        solar_pros = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(solar_pro_ids_to_query))
        for solar_pro in solar_pros:
            solar_pro_identifier_name_dict[solar_pro.identifier] = solar_pro.first_name.strip().title() + " " + solar_pro.last_name.strip().title()

        rep_id_name_dict = {}
        reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))
        for rep in reps:
            rep_id_name_dict[rep.rep_id] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

        logger_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(logger_kvs_to_query))
        for logger_kv in logger_kvs:
            data = json.loads(logger_kv.val)
            app_identifier = logger_kv.keyy.replace("_data_logging", "")
            idx = app_identifier_idx_dict[app_identifier]
            csv_rows[idx]["logger_deployed"] = str(data["logging"])

        app_identifier_system_cost_dict = {}
        sys_cost_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(sys_cost_kvs_to_query))
        for kv in sys_cost_kvs:
            app_identifier = kv.keyy.replace("total_system_cost_", "")
            value = str(kv.val)
            value = value.replace(",", "")
            value = value.replace("$", "")
            value = float(value)
            value = round(value, 2)
            value = Helpers.currency_format(value)
            app_identifier_system_cost_dict[app_identifier] = value


        funds = Helpers.list_funds()
        bookings = SurveyBooking.query(SurveyBooking.field_app_identifier.IN(app_ids_to_query))
        app_identifier_fund_dict = {}
        app_identifier_booking_dict = {}
        for booking in bookings:
            f = booking.fund
            value = "n/a"
            for fund in funds:
                if fund["value"] == f:
                    value = fund["value_friendly"]

            app_identifier_fund_dict[booking.field_app_identifier] = value
            app_identifier_booking_dict[booking.field_app_identifier] = booking

        app_identifier_proposal_dict = {}
        proposals = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(app_ids_to_query))
        for proposal in proposals:
            app_identifier_proposal_dict[proposal.field_app_identifier] = proposal

        pricing_structures = Helpers.get_pricing_structures()

        for obj in csv_rows:
            obj["solar_pro"] = solar_pro_identifier_name_dict[obj["solar_pro"]]
            obj["rep"] = rep_id_name_dict[obj["rep"]]
            obj["cd_date"] = app_identifier_cd_date_dict[obj["identifier"]]

            obj["welcome_call_date"] = "TBD"
            obj["install_date"] = "TBD"
            obj["fund"] = app_identifier_fund_dict[obj["identifier"]]

            pp_sub = app_identifier_pp_sub_dict[obj["identifier"]]
            info = json.loads(pp_sub.extra_info)

            if "project_management_checkoffs" in info.keys():
                if "welcome_call_completed" in info["project_management_checkoffs"].keys():
                    if "date" in info["project_management_checkoffs"]["welcome_call_completed"].keys():
                        obj["welcome_call_date"] = info["project_management_checkoffs"]["welcome_call_completed"]["date"]

                if "install" in info["project_management_checkoffs"].keys():
                    if "date" in info["project_management_checkoffs"]["install"].keys():
                        obj["install_date"] = info["project_management_checkoffs"]["install"]["date"]
            proposal = app_identifier_proposal_dict[obj["identifier"]]
            info2 = json.loads(proposal.info)
            production = float(info2["year_one_production"])
            original_panel_qty = float(info2["panel_qty"])
            new_panel_qty = float(str(original_panel_qty))
            if "new_panel_qty" in info2.keys():
                new_panel_qty = float(info2["new_panel_qty"])

            modified_production = (production * new_panel_qty) / original_panel_qty
            obj["production"] = str(round(modified_production, 2))

            office_identifier = app_identifier_office_identifier_dict[obj["identifier"]]
            market_key = office_identifier_market_identifier_dict[office_identifier]
            app_entry = app_identifier_app_entry_dict[obj["identifier"]]
            booking = app_identifier_booking_dict[obj["identifier"]]
            proposal.fix_additional_amount()
            proposal.fix_system_size()
            info3 = json.loads(proposal.info)
            obj["system_size"] = str(info3["system_size"])

            obj["total_system_cost"] = Helpers.currency_format(Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, info3, pricing_structures, funds))
            if app_entry.identifier in app_identifier_system_cost_dict.keys():
                obj["total_system_cost"] = app_identifier_system_cost_dict[app_entry.identifier]

        for obj in csv_rows:
            keys = obj.keys()
            for key in keys:
                value = obj[key]
                try:
                    value = str(value)
                except:
                    value = "Unsupported characters were present in this field"
                obj[key] = value

        headers = ('Name', 'Address', 'Phone', 'Email', 'Solar Pro', 'Rep', 'SP2 Time', 'CD Date', 'WC Date', 'Install Date', 'Last Year KWH', 'Fund', 'System Size', 'System Cost', 'System Production', 'Logger Deployed')
        data = []
        for row in csv_rows:
            data.append(
                    (row["name"], row["address"], row["phone"], row["email"], row["solar_pro"], row["rep"], row["sp2"], row["cd_date"], row["welcome_call_date"], row["install_date"], row["last_year_kwh_usage"], row["fund"], row["system_size"], row["total_system_cost"], row["production"], row["logger_deployed"])
                )

        import tablib
        structured_data = tablib.Dataset(*data, headers=headers)
        attachment_data = {}
        attachment_data["data"] = [base64.b64encode(structured_data.csv)]
        attachment_data["content_types"] = ["text/csv"]
        attachment_data["filenames"] = ["closed_deals" + str(start_dt).replace("-", "_") + str(end_dt).replace("-", "_") + ".csv"]

        Helpers.send_email(self.request.get("recipient"), "Your Data to Go Report", "See attached...", attachment_data)


    elif self.request.get("fn") == "new_hires":
        ninety_days_ago = Helpers.pacific_now() + timedelta(days=-90)
        reps = FieldApplicationUser.query(FieldApplicationUser.registration_date >= ninety_days_ago.date())
        rep_id_name_dict = {}
        rep_ids_to_query = ["-1"]
        rep_id_office_dict = {}
        rep_id_hire_date_dict = {}
        rep_id_hk_dict = {}
        rep_id_ab_dict = {}
        rep_id_ak_dict = {}
        rep_id_cd_dict = {}
        rep_ids = []
        for rep in reps:
            rep_id_name_dict[rep.rep_id] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
            rep_id_office_dict[rep.rep_id] = rep.main_office
            rep_id_hire_date_dict[rep.rep_id] = str(rep.registration_date)
            rep_id_hk_dict[rep.rep_id] = 0
            rep_id_ab_dict[rep.rep_id] = 0
            rep_id_ak_dict[rep.rep_id] = 0
            rep_id_cd_dict[rep.rep_id] = 0
            rep_ids.append(rep.rep_id)

        keys = ["hours_knocked_v2", "leads_acquired", "appointments_kept", "packets_submitted"]

        stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.dt >= ninety_days_ago,
                LeaderBoardStat.metric_key.IN(keys)
            )
        )
        for stat in stats:
            rep_id = stat.rep_id
            if rep_id in rep_ids:
                rep_id_hk_dict[stat.rep_id] += int(stat.metric_key == "hours_knocked_v2")
                rep_id_ab_dict[stat.rep_id] += int(stat.metric_key == "leads_acquired")
                rep_id_ak_dict[stat.rep_id] += int(stat.metric_key == "appointments_kept")
                rep_id_cd_dict[stat.rep_id] += int(stat.metric_key == "packets_submitted")


        rep_data = []
        for rep_id in rep_ids:
            obj = {}
            obj["name"] = rep_id_name_dict[rep_id]
            obj["hire_date"] = rep_id_hire_date_dict[rep_id]
            obj["hks"] = str(rep_id_hk_dict[rep_id])
            obj["abs"] = str(rep_id_ab_dict[rep_id])
            obj["aks"] = str(rep_id_ak_dict[rep_id])
            obj["cds"] = str(rep_id_cd_dict[rep_id])

            rep_data.append(obj)


        headers = ('Name', 'Hire Date', 'HKs', 'ABs', 'AKs', 'CDs', 'Best Dev')
        data = []
        for row in rep_data:
            data.append(
                    (row["name"], row["hire_date"], row["hks"], row["abs"], row["aks"], row["cds"], "Nirnberger")
                )

        import tablib
        structured_data = tablib.Dataset(*data, headers=headers)
        attachment_data = {}
        attachment_data["data"] = [base64.b64encode(structured_data.csv)]
        attachment_data["content_types"] = ["text/csv"]
        attachment_data["filenames"] = ["new_hire_insights_" + str(Helpers.pacific_today())]

        recipient = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
        if not recipient is None:
            Helpers.send_email(recipient.rep_email, "Your Data to Go Report", "See attached...", attachment_data)

        
    elif fn == "list_of_installs":
        year = int(self.request.get("year"))
        dt_start = datetime(year, 1, 1)
        dt_start = dt_start + timedelta(days=int(-365 * 0.666))
        dt_end = datetime(year, 12, 31, 23, 59, 59)

        customers = []

        pp_subs = PerfectPacketSubmission.query(
            ndb.AND(
                PerfectPacketSubmission.rep_submission_date >= dt_start,
                PerfectPacketSubmission.rep_submission_date <= dt_end
            )
        )

        app_ids_to_query = ["-1"]
        app_identifier_install_dt_dict = {}
        rep_ids_to_query = ["-1"]
        closer_ids_to_query = ["-5"]
        app_identifier_closer_dict = {}
        app_ids_with_closers = []
        pm_identifier_app_entry_list_dict = {}
        app_identifier_pm_dict = {}
        pm_ids_to_query = ["-1"]
        app_identifier_pto_received_dict = {}
        for pp_sub in pp_subs:
            info = json.loads(pp_sub.extra_info)

            if "project_manager" in info.keys():
                pm_ids_to_query.append(info["project_manager"])
                if not info["project_manager"] in pm_identifier_app_entry_list_dict.keys():
                    pm_identifier_app_entry_list_dict[info["project_manager"]] = []
                pm_identifier_app_entry_list_dict[info["project_manager"]].append(pp_sub.field_application_identifier)
                app_identifier_pm_dict[pp_sub.field_application_identifier] = info["project_manager"]

            if "project_management_checkoffs" in info.keys():
                if "install" in info["project_management_checkoffs"].keys():
                    if "date" in info["project_management_checkoffs"]["install"].keys():
                        if not info["project_management_checkoffs"]["install"]["date"] is None:
                            dt_vals = info["project_management_checkoffs"]["install"]["date"].split("-")
                            sub_year = int(dt_vals[0])

                            if sub_year == year:
                                if "checked" in info["project_management_checkoffs"]["install"].keys():
                                    if info["project_management_checkoffs"]["install"]:
                                        app_ids_to_query.append(pp_sub.field_application_identifier)
                                        rep_ids_to_query.append(pp_sub.rep_identifier)
                                        app_identifier_install_dt_dict[pp_sub.field_application_identifier] = info["project_management_checkoffs"]["install"]["date"]
                                        if "received_pto" in info["project_management_checkoffs"]:
                                            if "checked" in info["project_management_checkoffs"]["received_pto"].keys():
                                                if info["project_management_checkoffs"]["received_pto"]["checked"]:
                                                    if "date" in info["project_management_checkoffs"]["received_pto"].keys():
                                                        app_identifier_pto_received_dict[pp_sub.field_application_identifier] = info["project_management_checkoffs"]["received_pto"]["date"]

                                        if "closer" in info.keys():
                                            closer_ids_to_query.append(info["closer"])
                                            app_ids_with_closers.append(pp_sub.field_application_identifier)
                                            app_identifier_closer_dict[pp_sub.field_application_identifier] = info["closer"]        

        app_identifier_sys_size_dict = {}
        proposal_infos = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(app_ids_to_query))
        for p_info in proposal_infos:
            sub_info = json.loads(p_info.info)
            app_identifier_sys_size_dict[p_info.field_app_identifier] = sub_info["system_size"]

        pm_identifier_name_dict = {}
        project_managers = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(pm_ids_to_query))
        for pm in project_managers:
            pm_identifier_name_dict[pm.identifier] = pm.first_name.strip().title() + " " + pm.last_name.strip().title()

        rep_id_rep_name_dict = {"SHAF1021": "NP Admin"}
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
        for rep in reps:
            rep_id_rep_name_dict[rep.rep_id] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

        closer_identifier_name_dict = {}
        closers = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(closer_ids_to_query))
        for closer in closers:
            closer_identifier_name_dict[closer.identifier] = closer.first_name.strip().title() + " " + closer.last_name.strip().title()

        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        app_identifier_idx_dict_2 = {}
        app_identifier_signature_dict = {}
        signature_kv_keys_to_query = ["-5"]
        for app_entry in app_entries:
            try:
                obj = {"name": str(app_entry.customer_first_name.strip().title()) + " " + str(app_entry.customer_last_name.strip().title())}
            except:
                obj["name"] = "Unsupported special characters are present in this name. === " + app_entry.identifier + " ==="

            try:
                obj["identifier"] = app_entry.identifier
            except:
                obj["identifier"] = "-1"
            try:
                pm_id = app_identifier_pm_dict[app_entry.identifier]
                if app_entry.identifier in pm_identifier_app_entry_list_dict[pm_id]:
                    obj["project_manager"] = pm_identifier_name_dict[pm_id]
            except:
                obj["project_manager"] = "PM Unknown"

            try:
                obj["pto_received"] = app_identifier_pto_received_dict[app_entry.identifier]
            except:
                obj["pto_received"] = "Hold your horses"
            try:
                obj["address"] = str(app_entry.customer_address) + " " + str(app_entry.customer_city) + ", " + str(app_entry.customer_state) + " " + str(app_entry.customer_postal)
            except:
                obj["address"] = "Unsupported special characters are present in this address. === " + app_entry.identifier + " ==="

            try:
                obj["zip"] = str(app_entry.customer_postal)
            except:
                obj["zip"] = "Unsupported special characters are present in this postal code. === " + app_entry.identifier + " ==="

            try:
                obj["phone"] = Helpers.format_phone_number(str(app_entry.customer_phone))
            except:
               obj["phone"] =  "Unsupported special characters are present in this phone number. === " + app_entry.identifier + " ==="
            try:
                obj["email"] = str(app_entry.customer_email)
            except:
                obj["email"] = "Unsupported special characters are present in this email. === " + app_entry.identifier + " ==="

            try:
                obj["system_size"] = app_identifier_sys_size_dict[app_entry.identifier]
            except:
                obj["system_size"] = "0"

            if not app_entry.identifier in app_ids_with_closers:
                try:
                    obj["closer"] = str(rep_id_rep_name_dict[app_entry.rep_id])
                except:
                    obj["closer"] = "Unsupported special characters are present in this rep name. === " + app_entry.rep_id
            else:
                try:
                    closer = app_identifier_closer_dict[app_entry.identifier]
                    obj["closer"] = closer_identifier_name_dict[closer]
                except:
                    obj["closer"] = "Unsupported special characters are present in this rep name. === " + app_entry.rep_id

            obj["install_date"] = app_identifier_install_dt_dict[app_entry.identifier]

            app_identifier_idx_dict_2[app_entry.identifier] = len(customers)
            signature_kv_keys_to_query.append("customer_signature_" + app_entry.identifier)

            customers.append(obj)

        signature_kv_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(signature_kv_keys_to_query))
        for sig_item in signature_kv_items:
            a_identifier = sig_item.keyy.replace("customer_signature_", "")
            app_identifier_signature_dict[a_identifier] = str(sig_item.modified).split(".")[0]

        for customer in customers:
            try:
                customer["sig_dt"] = app_identifier_signature_dict[customer["identifier"]]
            except:
                customer["sig_dt"] = "1970-01-01 00:00:00"
        headers = ('Name', 'Closer', 'Address', 'Zip', 'Phone', 'Email', 'Install Date', 'Project Manager', 'PTO Received', 'Datetime Signed', 'System Size')
        data = []
        for item in customers:
            data.append(
                    (item["name"], item["closer"], item["address"], item["zip"], item["phone"], item["email"], item["install_date"], item['project_manager'], item['pto_received'], item['sig_dt'], item['system_size'])
                )

        import tablib
        structured_data = tablib.Dataset(*data, headers=headers)
        attachment_data = {}
        attachment_data["data"] = [base64.b64encode(structured_data.csv)]
        attachment_data["content_types"] = ["text/csv"]
        attachment_data["filenames"] = ["installs_list_" + str(dt_end.year) + ".csv"]
        Helpers.send_email(self.request.get("recipient"), "Your Data to Go Report", "See attached...", attachment_data)
    
    elif fn == "rep_aks_report":
        start_dt_vals = self.request.get("start_dt").split("-")
        end_dt_vals = self.request.get("end_dt").split("-")

        s_dt = datetime(int(start_dt_vals[0]), int(start_dt_vals[1]), int(start_dt_vals[2]))
        e_dt = datetime(int(end_dt_vals[0]), int(end_dt_vals[1]), int(end_dt_vals[2]), 23, 59, 59)

        stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "appointments_kept",
                LeaderBoardStat.dt >= s_dt,
                LeaderBoardStat.dt <= e_dt
            )
        )

        keepers = []
        rep_id_name_dict = {}
        users = FieldApplicationUser.query(
            ndb.AND(
                FieldApplicationUser.current_status == 0,
                FieldApplicationUser.user_type.IN(["energy_expert", "sales_manager"])
            )
        )

        for user in users:
            rep_id_name_dict[user.rep_id] = user.first_name.strip().title() + " " + user.last_name.strip().title()
            keepers.append(user.rep_id)

        rep_id_data_dict = {}
        app_identifier_rep_id_dict = {}
        app_ids_to_query = ["-2"]
        for stat in stats:
            if stat.rep_id in keepers:
                if not stat.rep_id in rep_id_data_dict.keys():
                    rep_id_data_dict[stat.rep_id] = []
                obj = {"identifier": stat.identifier, "field_app_identifier": stat.field_app_identifier, "cd": False, "address": "Error", "city": "Error", "state": "Error", "postal": "Error", "name": "Error", "sp2": "1970-01-01 00:00:00"}
                rep_id_data_dict[stat.rep_id].append(obj)
                app_identifier_rep_id_dict[stat.field_app_identifier] = stat.rep_id                
                if not stat.field_app_identifier in app_ids_to_query:
                    app_ids_to_query.append(stat.field_app_identifier)

        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        for app_entry in app_entries:
            identifier = app_entry.identifier
            rep_id_key = app_identifier_rep_id_dict[identifier]
            if rep_id_key in rep_id_data_dict.keys():
                for obj in rep_id_data_dict[rep_id_key]:
                    if obj["field_app_identifier"] == identifier:
                        obj["address"] = app_entry.customer_address.strip().title()
                        obj["city"] = app_entry.customer_city.strip().title()
                        obj["state"] = app_entry.customer_state.strip().title()
                        obj["postal"] = app_entry.customer_postal
                        obj["sp2"] = str(app_entry.sp_two_time).split(" ")[0]
                        obj["name"] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()

        cd_stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.field_app_identifier.IN(app_ids_to_query),
                LeaderBoardStat.metric_key == "packets_submitted"
            )
        )

        for stat in cd_stats:
            identifier = stat.field_app_identifier
            rep_id_key = app_identifier_rep_id_dict[identifier]

            if rep_id_key in rep_id_data_dict.keys():
                for obj in rep_id_data_dict[rep_id_key]:
                    if obj["field_app_identifier"] == stat.field_app_identifier:
                        obj["cd"] = True

        final_objects = []
        for rep_id in rep_id_data_dict.keys():
            for obj in rep_id_data_dict[rep_id]:
                new_obj = {}
                new_obj["rep_name"] = rep_id_name_dict[rep_id]
                new_obj["SP2"] = obj["sp2"]
                new_obj["customer_name"] = obj["name"]
                new_obj["customer_address"] = obj["address"]
                new_obj["city"] = obj["city"]
                new_obj["state"] = obj["state"]            
                new_obj["postal"] = obj["postal"]
                new_obj["CD"] = "No"
                if obj["cd"]:
                    new_obj["CD"] = "Yes"
                final_objects.append(new_obj)

        import tablib

        headers = ('Rep', 'SP2', 'Customer Name', 'Customer Address', 'Customer City', 'Customer State', 'Customer Postal', 'CD')
        csv_data = []
        for obj in final_objects:
            csv_data.append((obj["rep_name"],
                obj["SP2"],
                obj["customer_name"],
                obj["customer_address"],
                obj["city"],
                obj["state"],
                obj["postal"],
                obj["CD"]))

        structured_data = tablib.Dataset(*csv_data, headers=headers)

        attachment_data = {}
        attachment_data["data"] = [base64.b64encode(structured_data.csv)]
        attachment_data["content_types"] = ["text/csv"]
        attachment_data["filenames"] = ["rep_aks_" + str(s_dt).replace("-", "_") + "__" + str(e_dt).replace("-", "_") + ".csv"]
        
        Helpers.send_email(self.request.get("recipient"), "Rep AKs Report | " + str(s_dt) + " --- " + str(e_dt), "See attached...", attachment_data) 



    elif fn == "weekly_surveys":
        typ = self.request.get("type")
        dt_vals = self.request.get("start_dt").split("-")
        dt = date(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
        if typ == "ees+sms":
            rep_identifier_data_dict = {}
            rep_ids_to_query = ["-1"]            
            surveys = WeeklySurvey.query(
                ndb.AND(
                    WeeklySurvey.week_dt == dt,
                    WeeklySurvey.user_type.IN(["energy_expert", "sales_manager"])
                )
            )
            for survey in surveys:
                rep_identifier_data_dict[survey.rep_identifier] = {"data": json.loads(survey.response), "name": "", "dt": str(survey.submitted).split(".")[0]}
                rep_ids_to_query.append(survey.rep_identifier)

            reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
            for rep in reps:
                rep_identifier_data_dict[rep.identifier]["name"] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

            headers = ('Name', 'Personal HKs', 'Personal ABs', 'Personal AKs', 'Personal CDs', 'Personal Days Taken', 'Personal Days Requested', 'Sick Days Taken', 'Miles Driven', 'Hit 24 PHs?', 'Reason for sub-par PHs', 'Closing Percentage', 'PH Goal', 'CD Goal', 'How can we Help?', 'Timestamp')
            data = []

            
            for key in rep_identifier_data_dict.keys():
                item = rep_identifier_data_dict[key]

                for key2 in item["data"].keys():
                    string_value = item["data"][key2]
                    new_string_value = ""
                    for s in string_value:
                        try:
                            cpy = str(s)
                            new_string_value += cpy
                        except:
                            x = 5
                    item["data"][key2] = new_string_value


                data.append(
                        (item["name"], 
                        item["data"]["personal_hks"], 
                        item["data"]["personal_abs"],
                        item["data"]["personal_aks"],
                        item["data"]["personal_cds"],
                        item["data"]["personal_days_taken"],
                        item["data"]["personal_days_requested"],
                        item["data"]["sick_days_taken"],
                        item["data"]["miles_driven"],
                        item["data"]["ph_sel_24"],
                        item["data"]["reason_for_lower_ph"],
                        item["data"]["closing_percentage"],
                        item["data"]["this_week_phs"], 
                        item["data"]["this_week_cds"], 
                        item["data"]["how_can_we_help_you"],
                        item["dt"])
                    )

            import tablib
            structured_data = tablib.Dataset(*data, headers=headers)
            attachment_data = {}
            attachment_data["data"] = [base64.b64encode(structured_data.csv)]
            attachment_data["content_types"] = ["text/csv"]
            attachment_data["filenames"] = ["energy_expert_sales_manager_surveys_" + str(dt).replace("-", "_") + ".csv"]

            Helpers.send_email(self.request.get("recipient"), "Weekly Survey", "See attached...", attachment_data) 

        elif typ == "spms":
            rep_identifier_data_dict = {}
            rep_ids_to_query = ["-1"]            
            surveys = WeeklySurvey.query(
                ndb.AND(
                    WeeklySurvey.week_dt == dt,
                    WeeklySurvey.user_type == "solar_pro_manager"
                )
            )
            for survey in surveys:
                rep_identifier_data_dict[survey.rep_identifier] = {"data": json.loads(survey.response), "name": "", "dt": str(survey.submitted).split(".")[0]}
                rep_ids_to_query.append(survey.rep_identifier)

            reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
            for rep in reps:
                rep_identifier_data_dict[rep.identifier]["name"] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

            headers = ('Name', 'Office', 'Personal HKs', 'Personal ABs', 'Personal AKs', 'Personal CDs', 'Sick Days Taken', 'Got 20 HKs', 'Reason for Under 20 HKs', 'Team HKs', 'Team ABs', 'Team AKs', 'Plan for underperformers', 'Meetings Attended', 'Days of Perfect Power Hour', 'Team Activity?', 'Meal Goal Met', 'Team Meal Location and Time', 'Personal AK Goal', 'Team AK Goal', 'How can we help you?', 'Timestamp')
            data = []

            
            for key in rep_identifier_data_dict.keys():
                item = rep_identifier_data_dict[key]

                for key2 in item["data"].keys():
                    string_value = item["data"][key2]
                    new_string_value = ""
                    for s in string_value:
                        try:
                            cpy = str(s)
                            new_string_value += cpy
                        except:
                            x = 5
                    item["data"][key2] = new_string_value

                data.append(
                        (item["name"], 
                        item["data"]["office"], 
                        item["data"]["personal_hks"],
                        item["data"]["personal_abs"],
                        item["data"]["personal_aks"],
                        item["data"]["personal_cds"],
                        item["data"]["sick_days"],
                        item["data"]["twenty_hks_y_n"],
                        item["data"]["reason_for_failed_to_hit_20_hks"],
                        item["data"]["team_hks"],
                        item["data"]["team_abs"],
                        item["data"]["team_aks"],
                        item["data"]["underperformers"],
                        item["data"]["meeting_qty"],
                        item["data"]["perfect_power_hour"],
                        item["data"]["had_activity"],
                        item["data"]["dinner_goal"],
                        item["data"]["meal_goal_location"],
                        item["data"]["personal_ak_goal"],
                        item["data"]["meal_ak_goal"],
                        item["data"]["how_we_can_help"],
                        item["dt"])
                    )

            import tablib
            structured_data = tablib.Dataset(*data, headers=headers)
            attachment_data = {}
            attachment_data["data"] = [base64.b64encode(structured_data.csv)]
            attachment_data["content_types"] = ["text/csv"]
            attachment_data["filenames"] = ["spm_surveys_" + str(dt).replace("-", "_") + ".csv"]

            Helpers.send_email(self.request.get("recipient"), "Weekly Survey", "See attached...", attachment_data)


