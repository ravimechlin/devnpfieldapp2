def thomas_report1(self):
    import tablib
    from datetime import datetime
    import base64
    
    eligible_rep_ids = [""]
    reps = FieldApplicationUser.query()
    rep_id_rep_name_dict = {}
    for rep in reps:
        #if rep.user_type == "super":
        #    skip = "skip"
        #else:
        eligible_rep_ids.append(rep.rep_id)
        rep_id_rep_name_dict[rep.rep_id] = rep.first_name + " " + rep.last_name

    
    field_app_identifier_ab_date_dict = {}
    start_dt = datetime(int(self.request.get("floor_year")), int(self.request.get("floor_month")), int(self.request.get("floor_day")))    
    end_dt = datetime(int(self.request.get("ceiling_year")), int(self.request.get("ceiling_month")), int(self.request.get("ceiling_day")))
    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.metric_key == "leads_acquired",
            LeaderBoardStat.dt >= start_dt,
            LeaderBoardStat.dt <= end_dt
        )                   
    )
    app_ids_to_query = ["-1"]
    for stat in stats:
        if stat.rep_id in eligible_rep_ids:
            app_ids_to_query.append(stat.field_app_identifier)
            field_app_identifier_ab_date_dict[stat.field_app_identifier] = stat.dt

    customers = []
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    bad_identifiers = ["-1"]
    rep_ids_to_query = ["-1"]
    for app_entry in app_entries:
        if app_entry.lead_generator == "-1" or (app_entry.processed == 1 and app_entry.lead_generator != "-1"):
            try:
                obj = {"Name": str(app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title())}
            except:
                obj = {"Name": ""}
                bad_identifiers.append(app_entry.identifier)

            obj["Phone"] = Helpers.format_phone_number(app_entry.customer_phone)
            obj["Email"] = app_entry.customer_email
            try:
                obj["Address"] = str(app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal)
            except:
                obj["Address"] = ""
                if not app_entry.identifier in bad_identifiers:
                    bad_identifiers.append(app_entry.identifier)
            
            
            obj["AB Date"] = field_app_identifier_ab_date_dict[app_entry.identifier].strftime("%m/%d/%Y %I:%M %P")
            obj["SP2 Date"] = app_entry.sp_two_time.strftime("%m/%d/%Y %I:%M %P")
            obj["insert_time"] = app_entry.insert_time
            obj["rep"] = rep_id_rep_name_dict[app_entry.rep_id]

            customers.append(obj)

    if len(bad_identifiers) > 1:
        Helpers.send_email("rnirnber@gmail.com", "bad ids 2", json.dumps(bad_identifiers))

    customers = Helpers.bubble_sort(customers, "insert_time")

    headers = ('Name', 'Rep', 'Address', 'Phone', 'Email', '', "AB Date", "SP2 Date")
    data = []
    for customer in customers:
        data.append((customer["Name"],
                customer["rep"],
                customer["Address"],
                customer["Phone"],
                customer["Email"],
                '',
                customer["AB Date"],
                customer["SP2 Date"]))

    structured_data = tablib.Dataset(*data, headers=headers)
    attachment_data = {}
    attachment_data["data"] = [base64.b64encode(structured_data.csv)]
    attachment_data["content_types"] = ["text/csv"]
    attachment_data["filenames"] = ["leads.csv"]
    
    Helpers.send_email(self.request.get("delivery"), "Your Leads", "See attached file", attachment_data)

