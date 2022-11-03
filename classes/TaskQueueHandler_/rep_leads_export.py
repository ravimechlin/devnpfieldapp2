def rep_leads_export(self):
    import tablib
    from google.appengine.api import app_identity
    import base64

    items = []
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.rep_id == self.request.get("rep_id"))
    cnt = 0
    field_app_identifier_idx_dict = {}
    field_app_ids_to_query = ["-1"]
    bad_identifiers = ["-1"]
    for app_entry in app_entries:
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

        obj["AB Date"] = "1970-01-01"
        obj["SP2 Date"] = app_entry.sp_two_time.strftime("%m/%d/%Y %I:%M %P")
        obj["insert_time"] = app_entry.insert_time
        field_app_identifier_idx_dict[app_entry.identifier] = cnt
        field_app_ids_to_query.append(app_entry.identifier)
        items.append(obj)
        cnt += 1
    if len(bad_identifiers) > 1:
        #Helpers.send_email("rnirnber@gmail.com", "bad ids", json.dumps(bad_identifiers))
        xxx = "xxx"

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.metric_key == "leads_acquired",
            LeaderBoardStat.field_app_identifier.IN(field_app_ids_to_query)
        )
    )

    for stat in stats:
        items[field_app_identifier_idx_dict[stat.field_app_identifier]]["AB Date"] = stat.dt.strftime("%m/%d/%Y %I:%M %P")

    items = Helpers.bubble_sort(items, "insert_time")
    items.reverse()

    headers = ('Name', 'Address', 'Phone', 'Email', '', "AB Date", "SP2 Date")
    data = []
    for item in items:
        data.append((str(item["Name"]),
                str(item["Address"]),
                str(item["Phone"]),
                str(item["Email"]),
                '',
                str(item["AB Date"]),
                str(item["SP2 Date"])))

    structured_data = tablib.Dataset(*data, headers=headers)
    attachment_data = {}
    attachment_data["data"] = [base64.b64encode(structured_data.csv)]
    attachment_data["content_types"] = ["text/csv"]
    attachment_data["filenames"] = ["leads.csv"]

    rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == self.request.get("rep_id"))
    if not rep is None:
        Helpers.send_email(rep.rep_email, "Your Leads", "See attached file", attachment_data)


