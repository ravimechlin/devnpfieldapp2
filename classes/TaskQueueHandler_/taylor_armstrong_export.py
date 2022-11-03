def taylor_armstrong_export(self):
    import json
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.rep_id == "ARMS0717")
    data = []
    for app_entry in app_entries:
        obj = {}
        obj["name"] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
        obj["phone"] = Helpers.format_phone_number(app_entry.customer_phone)
        obj["email"] = app_entry.customer_email
        obj["address"] = app_entry.customer_address
        obj["city"] = app_entry.customer_city + ", " + app_entry.customer_state
        obj["postal"] = app_entry.customer_postal
        obj["sp2"] = str(app_entry.sp_two_time)
        data.append(obj)

    f = GCSLockedFile("/taylor_armstrong.json")
    f.write(json.dumps(data), "text/plain", "public-read")
