def get_customers_for_pm_tab_v2(self):
    self.response.content_type = "application/json"
    ret_json = {}
    ret_json["unassigned"] = []
    ret_json["pto_received"] = []
    ret_json["projects"] = {}
    ret_json["pm_identifier_name_dict"] = {}
    ret_json["pending_electricals"] = []
    ret_json["all_identifiers"] = []
    ret_json["all_projects"] = []
    pms = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.current_status == 0,
            FieldApplicationUser.is_project_manager == True
        )
    )
    for pm in pms:
        ret_json["pm_identifier_name_dict"][pm.identifier] = pm.first_name.strip().title() + " " + pm.last_name.strip().title()
        ret_json["projects"][pm.identifier] = {}
        ret_json["projects"][pm.identifier]["stage_1"] = []
        ret_json["projects"][pm.identifier]["stage_2"] = []
        ret_json["projects"][pm.identifier]["stage_3"] = []
        ret_json["projects"][pm.identifier]["stage_4"] = []
        ret_json["projects"][pm.identifier]["stage_5"] = []
        ret_json["projects"][pm.identifier]["stage_6"] = []

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
    app_identifier_address_dict = {}
    app_identifier_city_dict = {}
    app_identifier_state_dict = {}
    app_identifier_panel_work_completed_dict = {}
    app_identifier_panel_work_needed_dict = {}
    app_identifier_attachment_type_dict = {}
    app_identifier_signed_days_dict = {}
    app_identifier_postal_dict = {};
    signing_kvs_to_query = ["-1110011"]
    for app_entry in app_entries:
        app_ids_to_query.append(app_entry.identifier)
        app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
        app_identifier_address_dict[app_entry.identifier] = app_entry.customer_address
        app_identifier_city_dict[app_entry.identifier] = app_entry.customer_city
        app_identifier_state_dict[app_entry.identifier] = app_entry.customer_state
        app_identifier_panel_work_completed_dict[app_entry.identifier] = False
        app_identifier_panel_work_needed_dict[app_entry.identifier] = False
        app_identifier_attachment_type_dict[app_entry.identifier] = "N/A"
        app_identifier_postal_dict[app_entry.identifier] = app_entry.customer_postal
        signing_kvs_to_query.append("customer_signature_" + app_entry.identifier)
        app_identifier_signed_days_dict[app_entry.identifier] = -1

    now = Helpers.pacific_now()
    signing_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(signing_kvs_to_query))
    for s in signing_kvs:
        modified = s.modified
        seconds = float((now - modified).total_seconds())
        days =  int(seconds / float(86400))
        app_identifier_signed_days_dict[s.keyy.split("_")[2]] = days

    pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.field_application_identifier.IN(app_ids_to_query))
    for pp_sub in pp_subs:
        info = json.loads(pp_sub.extra_info)
        
        if "extra_project_specifics" in info.keys():
            keys_to_search = ["meter_spot_completed", "mpu_completed", "rma/gma_completed", "derate_completed", "bus_certification_completed"]
            keys_found = []

            for extra_item in info["extra_project_specifics"]:
                if extra_item["key"] in keys_to_search:
                    keys_found.append(extra_item["key"])

            found_tally = 0
                
            if "project_management_checkoffs" in info.keys():
                for key in keys_found:
                    if key in info["project_management_checkoffs"].keys():
                    	found_tally += int(("checked" in info["project_management_checkoffs"][key].keys() and info["project_management_checkoffs"][key]["checked"]) or ("date" in info["project_management_checkoffs"][key].keys() and "1800" in info["project_management_checkoffs"][key]["date"]))
                    	
            if (not found_tally == len(keys_found)):
                ret_json["pending_electricals"].append({"name": app_identifier_name_dict[pp_sub.field_application_identifier], "identifier": pp_sub.field_application_identifier})
                
        if "project_management_specifics" in info.keys():
            if "electrical" in info["project_management_specifics"].keys():
                app_identifier_panel_work_completed_dict[pp_sub.field_application_identifier] = True
                if "panel_work_required" in info["project_management_specifics"]["electrical"].keys():
                    app_identifier_panel_work_needed_dict[pp_sub.field_application_identifier] = info["project_management_specifics"]["electrical"]["panel_work_required"]
                if "attachment_type" in info["project_management_specifics"]["electrical"].keys():
                    app_identifier_attachment_type_dict[pp_sub.field_application_identifier] = info["project_management_specifics"]["electrical"]["attachment_type"]

        append_to = ret_json["unassigned"]

        ret_json["all_identifiers"].append(pp_sub.field_application_identifier)

        if "project_manager" in info.keys():
            pm_identifier = info["project_manager"]
            if pm_identifier in ret_json["pm_identifier_name_dict"].keys():                
                append_to = ret_json["projects"][pm_identifier]["stage_1"]
                
            else:
                append_to = ret_json["unassigned"]
                old_pm = FieldApplicationUser.first(FieldApplicationUser.identifier == pm_identifier)
                if not old_pm is None:
                    ret_json["pm_identifier_name_dict"][old_pm.identifier] = old_pm.first_name.strip().title() + " " + old_pm.last_name.strip().title()
                    ret_json["projects"][old_pm.identifier] = {}
                    ret_json["projects"][old_pm.identifier]["stage_1"] = []
                    ret_json["projects"][old_pm.identifier]["stage_2"] = []
                    ret_json["projects"][old_pm.identifier]["stage_3"] = []
                    ret_json["projects"][old_pm.identifier]["stage_4"] = []
                    ret_json["projects"][old_pm.identifier]["stage_5"] = []
                    ret_json["projects"][old_pm.identifier]["stage_6"] = []            

        is_pto = False
        if "project_management_checkoffs" in info.keys():            
            if "received_pto" in info["project_management_checkoffs"].keys():
                if "checked" in info["project_management_checkoffs"]["received_pto"].keys():
                    if info["project_management_checkoffs"]["received_pto"]["checked"]:
                        append_to = ret_json["pto_received"]
                        is_pto = True


            if not is_pto:
                if "welcome_call_completed" in info["project_management_checkoffs"].keys():
                    
                    if ("checked" in info["project_management_checkoffs"]["welcome_call_completed"].keys() and info["project_management_checkoffs"]["welcome_call_completed"]["checked"]) or ("date" in info["project_management_checkoffs"]["welcome_call_completed"].keys() and ("1800" in info["project_management_checkoffs"]["welcome_call_completed"]["date"])):
                        if "welcome_email_sent" in info["project_management_checkoffs"].keys():                            
                            if ("checked" in info["project_management_checkoffs"]["welcome_email_sent"].keys() and info["project_management_checkoffs"]["welcome_email_sent"]["checked"]) or ("date" in info["project_management_checkoffs"]["welcome_email_sent"].keys() and ("1800" in info["project_management_checkoffs"]["welcome_email_sent"]["date"])):
                                if "first_payment_received" in info["project_management_checkoffs"].keys():                                    
                                    if ("checked" in info["project_management_checkoffs"]["first_payment_received"].keys() and info["project_management_checkoffs"]["first_payment_received"]["checked"]) or ("date" in info["project_management_checkoffs"]["first_payment_received"].keys() and ("1800" in info["project_management_checkoffs"]["first_payment_received"]["date"])):
                                        if "ntp" in info["project_management_checkoffs"].keys():
                                            if ("checked" in info["project_management_checkoffs"]["ntp"].keys() and info["project_management_checkoffs"]["ntp"]["checked"]) or ("date" in info["project_management_checkoffs"]["ntp"].keys() and ("1800" in info["project_management_checkoffs"]["ntp"]["date"])):                                                
                                                if pm_identifier in ret_json["pm_identifier_name_dict"].keys():
                                                    append_to = ret_json["projects"][pm_identifier]["stage_2"]
                                                else:
                                                    append_to = ret_json["unassigned"]
                                                    old_pm = FieldApplicationUser.first(FieldApplicationUser.identifier == pm_identifier)
                                                    if not old_pm is None:
                                                        ret_json["pm_identifier_name_dict"][old_pm.identifier] = old_pm.first_name.strip().title() + " " + old_pm.last_name.strip().title()
                                                        ret_json["projects"][old_pm.identifier] = {}
                                                        ret_json["projects"][old_pm.identifier]["stage_1"] = []
                                                        ret_json["projects"][old_pm.identifier]["stage_2"] = []
                                                        ret_json["projects"][old_pm.identifier]["stage_3"] = []
                                                        ret_json["projects"][old_pm.identifier]["stage_4"] = []
                                                        ret_json["projects"][old_pm.identifier]["stage_5"] = []
                                                        ret_json["projects"][old_pm.identifier]["stage_6"] = []

                                                if "panel_assessment" in info["project_management_checkoffs"].keys():
                                                    if ("checked" in info["project_management_checkoffs"]["panel_assessment"].keys() and info["project_management_checkoffs"]["panel_assessment"]["checked"]) or ("date" in info["project_management_checkoffs"]["panel_assessment"].keys() and ("1800" in info["project_management_checkoffs"]["panel_assessment"]["date"])):
                                                        if "plan_set_in_progress" in info["project_management_checkoffs"].keys():                                                    
                                                            if("checked" in info["project_management_checkoffs"]["plan_set_in_progress"].keys() and info["project_management_checkoffs"]["plan_set_in_progress"]["checked"]) or ("date" in info["project_management_checkoffs"]["plan_set_in_progress"].keys() and ("1800" in info["project_management_checkoffs"]["plan_set_in_progress"]["date"])):
                                                                if "plan_set_completed" in info["project_management_checkoffs"].keys():
                                                                    if("checked" in  info["project_management_checkoffs"]["plan_set_completed"].keys() and info["project_management_checkoffs"]["plan_set_completed"]["checked"]) or ("date" in info["project_management_checkoffs"]["plan_set_completed"].keys() and ("1800" in info["project_management_checkoffs"]["plan_set_completed"]["date"])):
                                                                        if "pe_stamps_ordered" in info["project_management_checkoffs"].keys():       
                                                                            if("checked" in  info["project_management_checkoffs"]["pe_stamps_ordered"].keys() and info["project_management_checkoffs"]["pe_stamps_ordered"]["checked"]) or ("date" in info["project_management_checkoffs"]["pe_stamps_ordered"].keys() and ("1800" in info["project_management_checkoffs"]["pe_stamps_ordered"]["date"])):
                                                                                if "pe_stamps_received" in info["project_management_checkoffs"].keys():                                                                            
                                                                                    if("checked" in  info["project_management_checkoffs"]["pe_stamps_received"].keys() and info["project_management_checkoffs"]["pe_stamps_received"]["checked"]) or ("date" in info["project_management_checkoffs"]["pe_stamps_received"].keys() and ("1800" in info["project_management_checkoffs"]["pe_stamps_received"]["date"])):
                                                                                        if pm_identifier in ret_json["pm_identifier_name_dict"].keys():
                                                                                            append_to = ret_json["projects"][pm_identifier]["stage_3"]
                                                                                        else:
                                                                                            append_to = ret_json["unassigned"]
                                                                                            old_pm = FieldApplicationUser.first(FieldApplicationUser.identifier == pm_identifier)
                                                                                            if not old_pm is None:
                                                                                                ret_json["pm_identifier_name_dict"][old_pm.identifier] = old_pm.first_name.strip().title() + " " + old_pm.last_name.strip().title()
                                                                                                ret_json["projects"][old_pm.identifier] = {}
                                                                                                ret_json["projects"][old_pm.identifier]["stage_1"] = []
                                                                                                ret_json["projects"][old_pm.identifier]["stage_2"] = []
                                                                                                ret_json["projects"][old_pm.identifier]["stage_3"] = []
                                                                                                ret_json["projects"][old_pm.identifier]["stage_4"] = []
                                                                                                ret_json["projects"][old_pm.identifier]["stage_5"] = []
                                                                                                ret_json["projects"][old_pm.identifier]["stage_6"] = []

                                                                                        if "equipment_ordered" in info["project_management_checkoffs"].keys():
                                                                                            if ("checked" in info["project_management_checkoffs"]["equipment_ordered"].keys() and info["project_management_checkoffs"]["equipment_ordered"]["checked"]) or ("date" in info["project_management_checkoffs"]["equipment_ordered"].keys() and ("1800" in info["project_management_checkoffs"]["equipment_ordered"]["date"])):
                                                                                                if "placards_ordered" in info["project_management_checkoffs"].keys():
                                                                                                    if ("checked" in info["project_management_checkoffs"]["placards_ordered"].keys() and info["project_management_checkoffs"]["placards_ordered"]["checked"]) or ("date" in info["project_management_checkoffs"]["placards_ordered"].keys() and ("1800" in info["project_management_checkoffs"]["placards_ordered"]["date"])):
                                                                                                        if "permit_to_city" in info["project_management_checkoffs"].keys():
                                                                                                            if ("checked" in info["project_management_checkoffs"]["permit_to_city"].keys() and  info["project_management_checkoffs"]["permit_to_city"]["checked"]) or ("date" in info["project_management_checkoffs"]["permit_to_city"].keys() and ("1800" in info["project_management_checkoffs"]["permit_to_city"]["date"])):
                                                                                                                if "permit_status" in info["project_management_checkoffs"].keys():                                                                                                                    
                                                                                                                    if ("checked" in info["project_management_checkoffs"]["permit_status"].keys() and info["project_management_checkoffs"]["permit_status"]["checked"]) or ("date" in info["project_management_checkoffs"]["permit_status"].keys() and ("1800" in info["project_management_checkoffs"]["permit_status"]["date"])):                                                                                                                
                                                                                                                        if pm_identifier in ret_json["pm_identifier_name_dict"].keys():
                                                                                                                            append_to = ret_json["projects"][pm_identifier]["stage_4"]
                                                                                                                        else:
                                                                                                                            append_to = ret_json["unassigned"]
                                                                                                                            old_pm = FieldApplicationUser.first(FieldApplicationUser.identifier == pm_identifier)
                                                                                                                            if not old_pm is None:
                                                                                                                                ret_json["pm_identifier_name_dict"][old_pm.identifier] = old_pm.first_name.strip().title() + " " + old_pm.last_name.strip().title()
                                                                                                                                ret_json["projects"][old_pm.identifier] = {}
                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_1"] = []
                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_2"] = []
                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_3"] = []
                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_4"] = []
                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_5"] = []
                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_6"] = []

                                                                                                                        if "permits_with_contractor" in info["project_management_checkoffs"].keys():
                                                                                                                            if ("checked" in info["project_management_checkoffs"]["permits_with_contractor"].keys() and info["project_management_checkoffs"]["permits_with_contractor"]["checked"]) or ("date" in info["project_management_checkoffs"]["permits_with_contractor"].keys() and ("1800" in info["project_management_checkoffs"]["permits_with_contractor"]["date"])):
                                                                                                                                if "install" in info["project_management_checkoffs"].keys():                                                                                                                                            
                                                                                                                                    if ("checked" in info["project_management_checkoffs"]["install"].keys() and info["project_management_checkoffs"]["install"]["checked"]) or ("date" in info["project_management_checkoffs"]["install"].keys() and ("1800" in info["project_management_checkoffs"]["install"]["date"])):                                                                                                                                
                                                                                                                                        if "placards_received" in info["project_management_checkoffs"].keys():
                                                                                                                                            if ("checked" in info["project_management_checkoffs"]["placards_received"].keys() and info["project_management_checkoffs"]["placards_received"]["checked"]) or ("date" in info["project_management_checkoffs"]["placards_received"].keys() and ("1800" in info["project_management_checkoffs"]["placards_received"]["date"])):
                                                                                                                                                if pm_identifier in ret_json["pm_identifier_name_dict"].keys():
                                                                                                                                                    append_to = ret_json["projects"][pm_identifier]["stage_5"]
                                                                                                                                                else:
                                                                                                                                                    append_to = ret_json["unassigned"]
                                                                                                                                                    old_pm = FieldApplicationUser.first(FieldApplicationUser.identifier == pm_identifier)
                                                                                                                                                    if not old_pm is None:
                                                                                                                                                        ret_json["pm_identifier_name_dict"][old_pm.identifier] = old_pm.first_name.strip().title() + " " + old_pm.last_name.strip().title()
                                                                                                                                                        ret_json["projects"][old_pm.identifier] = {}
                                                                                                                                                        ret_json["projects"][old_pm.identifier]["stage_1"] = []
                                                                                                                                                        ret_json["projects"][old_pm.identifier]["stage_2"] = []
                                                                                                                                                        ret_json["projects"][old_pm.identifier]["stage_3"] = []
                                                                                                                                                        ret_json["projects"][old_pm.identifier]["stage_4"] = []
                                                                                                                                                        ret_json["projects"][old_pm.identifier]["stage_5"] = []
                                                                                                                                                        ret_json["projects"][old_pm.identifier]["stage_6"] = []


                                                                                                                                                if "final_inspection" in info["project_management_checkoffs"].keys():
                                                                                                                                                    if ("checked" in info["project_management_checkoffs"]["final_inspection"].keys() and info["project_management_checkoffs"]["final_inspection"]["checked"]) or ("date" in info["project_management_checkoffs"]["final_inspection"].keys() and ("1800" in info["project_management_checkoffs"]["final_inspection"]["date"])):                                                                                                                                                                                                                                                                                                                
                                                                                                                                                        if pm_identifier in ret_json["pm_identifier_name_dict"].keys():
                                                                                                                                                            append_to = ret_json["projects"][pm_identifier]["stage_6"]
                                                                                                                                                        else:
                                                                                                                                                            append_to = ret_json["unassigned"]
                                                                                                                                                            old_pm = FieldApplicationUser.first(FieldApplicationUser.identifier == pm_identifier)
                                                                                                                                                            if not old_pm is None:
                                                                                                                                                                ret_json["pm_identifier_name_dict"][old_pm.identifier] = old_pm.first_name.strip().title() + " " + old_pm.last_name.strip().title()
                                                                                                                                                                ret_json["projects"][old_pm.identifier] = {}
                                                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_1"] = []
                                                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_2"] = []
                                                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_3"] = []
                                                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_4"] = []
                                                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_5"] = []
                                                                                                                                                                ret_json["projects"][old_pm.identifier]["stage_6"] = []

        item = {"identifier": pp_sub.field_application_identifier}
        item["name"] = app_identifier_name_dict[pp_sub.field_application_identifier]
        item["address"] = app_identifier_address_dict[pp_sub.field_application_identifier]
        item["city"] = app_identifier_city_dict[pp_sub.field_application_identifier]
        item["postal"] = app_identifier_postal_dict[pp_sub.field_application_identifier]
        item["state"] = app_identifier_state_dict[pp_sub.field_application_identifier]
        item["panel_work_completed"] = app_identifier_panel_work_completed_dict[pp_sub.field_application_identifier]
        item["panel_work_needed"] = app_identifier_panel_work_needed_dict[pp_sub.field_application_identifier]
        item["days_ago"] = app_identifier_signed_days_dict[pp_sub.field_application_identifier]
        item["attachment_type"] = app_identifier_attachment_type_dict[pp_sub.field_application_identifier]
        item["pto_received"] = is_pto
        ret_json["all_projects"].append(item)
        append_to.append(item)

    self.response.out.write(json.dumps(ret_json))
