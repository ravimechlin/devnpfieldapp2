def marketing(self):
    now = Helpers.pacific_now()
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.insert_time >= 1513123200000)                                                                                 
    jaysawn = []
    for app_entry in app_entries:
        if app_entry.sp_two_time < now and (not app_entry.deal_closed):
            obj = {"first_name": app_entry.customer_first_name.strip().title()}
            obj["last_name"] = app_entry.customer_last_name.strip().title()
            obj["phone"] = Helpers.format_phone_number(app_entry.customer_phone)
            obj["email"] = app_entry.customer_email
            obj["address"] = app_entry.customer_address + "\n" + app_entry.customer_city + ", " + app_entry.customer_state + "\n" + app_entry.customer_postal
            jaysawn.append(obj)

    f = GCSLockedFile("/marketing.json")
    f.write(json.dumps(jaysawn), "text/plain", "public-read")

