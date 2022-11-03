def solar_pro_cds(self):
    from datetime import datetime
    import tablib
    start_dt_vals = self.request.get("start_dt").split("-")
    start_dt = datetime(int(start_dt_vals[0]), int(start_dt_vals[1]), int(start_dt_vals[2]))
    end_dt_vals = self.request.get("end_dt").split("-")
    end_dt = datetime(int(end_dt_vals[0]), int(end_dt_vals[1]), int(end_dt_vals[2]), 23, 59, 59)

    rep_identifier_rep_name_dict = {}
    rep_id_rep_name_dict = {}    

    users = FieldApplicationUser.query()
    for user in users:
        rep_identifier_rep_name_dict[user.identifier] = user.first_name + " " + user.last_name
        rep_id_rep_name_dict[user.rep_id] = user.first_name + " " + user.last_name

    app_ids_to_query = ["-1"]
    field_app_identifier_date_dict = {}
    field_app_identifier_rep_id_dict = {}
    stats = LeaderBoardStat.query(
        LeaderBoardStat.metric_key == "packets_submitted",
        LeaderBoardStat.dt >= start_dt,
        LeaderBoardStat.dt <= end_dt
    )

    #.strftime("%m/%d/%Y %I:%M %P")
    for stat in stats:
        field_app_identifier_date_dict[stat.field_app_identifier] = stat.dt
        field_app_identifier_rep_id_dict[stat.field_app_identifier] = stat.rep_id
        app_ids_to_query.append(stat.field_app_identifier)

    lst = []
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    for app_entry in app_entries:
        if not app_entry.lead_generator == "-1":
            obj = {"Customer Name": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()}
            obj["CD Date"] = field_app_identifier_date_dict[app_entry.identifier]
            obj["Rep"] = rep_id_rep_name_dict[field_app_identifier_rep_id_dict[app_entry.identifier]]
            obj["Solar Pro"] = rep_identifier_rep_name_dict[app_entry.lead_generator]
            obj["Address"] = app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state
            obj["Postal"] = app_entry.customer_postal
            lst.append(obj)

    lst = Helpers.bubble_sort(lst, "CD Date")
    lst_cpy = []
    for item in lst:
        item["CD Date"] = item["CD Date"].strftime("%m/%d/%Y %I:%M %P")

    headers = ('Customer Name', 'Customer Address', 'Customer Postal', 'CD Date', 'Rep', 'Solar Pro')
    data = []
    for item in lst:
        data.append((item["Customer Name"],
                item["Address"],
                item["Postal"],
                item["CD Date"],
                item["Rep"],
                item["Solar Pro"]))

    structured_data = tablib.Dataset(*data, headers=headers)
    attachment_data = {}
    attachment_data["data"] = [base64.b64encode(structured_data.csv)]
    attachment_data["content_types"] = ["text/csv"]
    attachment_data["filenames"] = ["solar_pro_cds_" + self.request.get("start_dt").replace("-", "_") + "__" + self.request.get("end_dt").replace("-", "_")]
    
    Helpers.send_email(self.request.get("email"), "Your Solar Pro CDs Report", "See attached...", attachment_data)
