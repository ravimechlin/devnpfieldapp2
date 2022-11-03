def leads_export(self):
    from datetime import datetime
    from datetime import timedelta
    from google.appengine.api import app_identity
    import cloudstorage as gcs
    import tablib

    start_vals = self.request.get("start").split("-")
    end_vals = self.request.get("end").split("-")
    email = self.request.get("email")
    start_dt = datetime(int(start_vals[0]), int(start_vals[1]), int(start_vals[2]))# + timedelta(hours=-8)
    end_dt = datetime(int(end_vals[0]), int(end_vals[1]), int(end_vals[2]), 23, 59, 59)# + timedelta(hours=8)

    epoch = datetime(1970, 1, 1)

    start_millis = int((start_dt - epoch).total_seconds()) * 1000
    end_millis = int((end_dt - epoch).total_seconds()) * 1000

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= start_dt,
            LeaderBoardStat.dt <= end_dt,
            LeaderBoardStat.metric_key == "leads_acquired"
        )
    )

    pre_app_ids_to_query = ["-1"]
    for stat in stats:
        pre_app_ids_to_query.append(stat.field_app_identifier)

    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(pre_app_ids_to_query))

    leads = []
    solar_pro_ids_to_query = ["-1"]
    rep_ids_to_query = ["-1"]
    app_ids_to_query = ["-1"]
    app_identifier_idx_dict = {}
    data = []
    logger_kv_keys_to_query = ["-1"]
    estimated_or_real_kvs_to_query = ["-1"]
    bulk_key_keys_to_query = ["-1"]   
    for app_entry in app_entries:
        if True:
        #if app_entry.is_lead and (not app_entry.lead_generator == "-1"):
            if not app_entry.rep_id in rep_ids_to_query:
                rep_ids_to_query.append(app_entry.rep_id)
            if not app_entry.lead_generator in solar_pro_ids_to_query:
                solar_pro_ids_to_query.append(app_entry.lead_generator)
            app_ids_to_query.append(app_entry.identifier)

            obj = {"name": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()}
            obj["address"] = app_entry.customer_address + "\r\n" + app_entry.customer_city + ", " + app_entry.customer_state + "\r\n" + app_entry.customer_postal
            obj["solar_pro"] = app_entry.lead_generator
            obj["rep"] = app_entry.rep_id
            obj["sp_two_time"] = str(app_entry.sp_two_time).split(".")[0]
            obj["status"] = "Not Available"
            obj["notes"] = "None Recorded"
            obj["AK"] = "No"
            obj["CD"] = "No"
            obj["CD_date"] = "1970-01-01"
            obj["system_size"] = "-1.0"
            obj["welcome_email_sent_box_checked"] = "No"
            obj["logger_deployed"] = "Not Available"
            obj["usage_type"] = "Not Available"
            obj["welfare"] = "No"
            obj["override_code_provided"] = "No"

            logger_kv_keys_to_query.append(app_entry.identifier + "_data_logging")
            estimated_or_real_kvs_to_query.append("original_real_or_estimated_" + app_entry.identifier)
            bulk_key_keys_to_query.append("ab_override_" + app_entry.identifier)

            app_identifier_idx_dict[app_entry.identifier] = len(data)
            data.append(obj)

    rep_id_rep_name_dict = {}
    reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))
    for rep in reps:
        rep_id_rep_name_dict[rep.rep_id] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

    for item in data:
        if item["rep"] in rep_id_rep_name_dict.keys():
            item["rep"] = rep_id_rep_name_dict[item["rep"]]

    solar_pro_identifier_name_dict = {"-1": "N/A"}
    solar_pros = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(solar_pro_ids_to_query))
    for solar_pro in solar_pros:
        solar_pro_identifier_name_dict[solar_pro.identifier] = solar_pro.first_name.strip().title() + " " + solar_pro.last_name.strip().title()

    for item in data:
        if item["solar_pro"] in solar_pro_identifier_name_dict.keys():
            item["solar_pro"] = solar_pro_identifier_name_dict[item["solar_pro"]]

    notes = CustomerNote.query(
        ndb.AND(
            CustomerNote.note_key.IN(["rep_lead_notes","welfare"]),
            CustomerNote.field_app_identifier.IN(app_ids_to_query)
        )
    )
    for note in notes:
        idx = app_identifier_idx_dict[note.field_app_identifier]
        if note.note_key == "rep_lead_notes":
            data[idx]["notes"] = unicode(json.loads(note.content)["txt"][0]).replace(u'\xd7', 'x').replace(u'\U0001f625', ":(")
            try:
                data[idx]["notes"] = str(data[idx]["notes"])
            except:
                data[idx]["notes"] = "Notes had emojis which are not supported."
        elif note.note_key == "welfare":
            data[idx]["welfare"] = "Yes"

    bulk_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(bulk_key_keys_to_query))
    for kv in bulk_kvs:
        if "ab_override_" in kv.keyy:
            idx = app_identifier_idx_dict[note.field_app_identifier]
            data[idx]["override_code_provided"] = "Yes"
    pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.field_application_identifier.IN(app_ids_to_query))
    for pp_sub in pp_subs:
        idx = app_identifier_idx_dict[pp_sub.field_application_identifier]
        info = json.loads(pp_sub.extra_info)
        if "project_management_checkoffs" in info.keys():
            if "welcome_email_sent" in info["project_management_checkoffs"].keys():
                if "checked" in info["project_management_checkoffs"]["welcome_email_sent"].keys():
                    if info["project_management_checkoffs"]["welcome_email_sent"]["checked"]:
                        data[idx]["welcome_email_sent_box_checked"] = "Yes"

    #stats = LeaderBoardStat.query(LeaderBoardStat.field_app_identifier.IN(app_ids_to_query))
    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.field_app_identifier.IN(app_ids_to_query),
            LeaderBoardStat.metric_key.IN(["appointments_kept", "packets_submitted"])
        )
    )
    for stat in stats:
        if not stat.field_app_identifier == "-1":
            idx = app_identifier_idx_dict[stat.field_app_identifier]
            if stat.metric_key == "appointments_kept":
                data[idx]["AK"] = "Yes"
            elif stat.metric_key == "packets_submitted":
                data[idx]["CD"] = "Yes"
                data[idx]["CD_date"] = str(stat.dt).split(".")[0]

    options_dict = {
                    "default": "Active",
                    "rescheduled": "Reschedule",
                    "lead_cancelled": "Lead Cancelled",
                    "no_contact_but_further_followup": "Not able to contact but will keep following up",
                    "no_contact_no_followup": "Not able to contact and not going to follow up",
                    "going_to_keep_following_up": "Going to keep following up"
            }

    leads = Lead.query(Lead.field_app_identifier.IN(app_ids_to_query))
    for lead in leads:
        idx = app_identifier_idx_dict[lead.field_app_identifier]
        if lead.status in options_dict.keys():
            data[idx]["status"] = options_dict[lead.status]

    proposals = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(app_ids_to_query))
    for proposal in proposals:
        try:
            proposal.fix_additional_amount()
            proposal.fix_system_size()
        except:
            x = 5
        info = json.loads(proposal.info)
        idx = app_identifier_idx_dict[proposal.field_app_identifier]
        if "system_size" in info.keys():
            data[idx]["system_size"] = str(info["system_size"])

    logger_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(logger_kv_keys_to_query))
    for kv in logger_kvs:
        logger_data = json.loads(kv.val)
        app_entry_identifier = kv.keyy.replace("_data_logging", "")
        idx = app_identifier_idx_dict[app_entry_identifier]
        if "id" in logger_data.keys():
            data[idx]["logger_deployed"] = "Yes"
        else:
            data[idx]["logger_deployed"] = "No"

    real_or_estimated_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(estimated_or_real_kvs_to_query))
    for kv in real_or_estimated_kvs:
        app_entry_identifier = kv.keyy.replace("original_real_or_estimated_", "")
        idx = app_identifier_idx_dict[app_entry_identifier]
        data[idx]["usage_type"] = kv.val

    xlsx_data = []
    headers = ('Name', 'Address', 'Solar Pro', 'Rep', 'SP2 Time', "Status", "Notes", "AK", "CD", "CD Date", "System Size", "Welcome Email Sent Box Currently Checked", "Logger Deployed", "Original Usage Type", "Care", "Care Override Code Provided")
    xlsx_data.append(('', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''))
    for item in data:
        xlsx_data.append(
            (item["name"], item["address"], item["solar_pro"], item["rep"], item["sp_two_time"], item["status"], item["notes"], item["AK"], item["CD"], item["CD_date"], item["system_size"], item["welcome_email_sent_box_checked"], item["logger_deployed"], item["usage_type"], item["welfare"], item["override_code_provided"])
        )

    structured_data = tablib.Dataset(*xlsx_data, headers=headers)
    file_id = hashlib.md5(Helpers.guid()).hexdigest()

    bucket_name = os.environ.get('BUCKET_NAME',
                                app_identity.get_default_gcs_bucket_name())

    bucket = '/' + bucket_name
    filename = bucket + '/LeadExports/' + file_id + ".csv"

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file = gcs.open(filename,
                        'w',
                        content_type="text/csv",
                        options={'x-goog-meta-foo': 'foo',
                                'x-goog-meta-bar': 'bar',
                                'x-goog-acl': 'public-read'
                        },
                        retry_params=write_retry_params)

    gcs_file.write(structured_data.csv)
    gcs_file.close()

    time.sleep(10)

    attachment_data = {}

    attachment_data["data"] = []
    attachment_data["content_types"] = []
    attachment_data["filenames"] = []

    attachment_data["data"].append("https://storage.googleapis.com/" + app_identity.get_application_id() + ".appspot.com/LeadExports/" + file_id + ".csv")
    attachment_data["content_types"].append("text/csv")
    attachment_data["filenames"].append(file_id + ".csv")

    debugging_file = GCSLockedFile("/debugging.txt")
    debugging_file.write(json.dumps(attachment_data), json.dumps(attachment_data), "public-read")
    debugging_file.unlock()

    msg = "Please see attached..."

    Helpers.send_email(email, "The Report You Requested - Lead Exports", msg, attachment_data)
    time.sleep(30)
    bucket_name = os.environ.get('BUCKET_NAME',
                            app_identity.get_default_gcs_bucket_name())

    bucket = '/' + bucket_name
    filename = bucket + "/LeadExports/" + file_id + ".csv"
    gcs.delete(filename)


