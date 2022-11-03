def pto_monthly_report(self):
    from datetime import datetime
    from datetime import timedelta
    import tablib

    month_mapping = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

    start_dt = datetime(int(self.request.get("year")), int(self.request.get("month")), 1)
    start_dt_cpy = datetime(start_dt.year, start_dt.month, start_dt.day)
    current_month = start_dt_cpy.month
    month_changed = False
    while not month_changed:
        start_dt_cpy = start_dt_cpy + timedelta(days=1)
        month_changed = not (start_dt_cpy.month == current_month)
    start_dt_cpy = start_dt_cpy + timedelta(days=-1)
    end_dt = datetime(start_dt_cpy.year, start_dt_cpy.month, start_dt_cpy.day, 23, 59, 59)

    six_months_ago = Helpers.pacific_now() + timedelta(days=-31 * 6)
    six_months_ago = datetime(six_months_ago.year, six_months_ago.month, six_months_ago.day)

    now = int(time.time())
    two_years_ago = now - int(60 * 60 * 24 * 365 * 1.5)
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.insert_time >= two_years_ago)
    app_identifier_name_dict = {}
    app_identifier_phone_dict = {}
    app_identifier_address_dict = {}
    app_identifier_city_dict = {}
    app_identifier_state_dict = {}
    app_identifier_postal_dict = {}

    customers = []
    six_months_ago_customers = []

    app_ids_to_query = ["-1"]
    for app_entry in app_entries:
        if app_entry.deal_closed:
            app_ids_to_query.append(app_entry.identifier)
            app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
            app_identifier_phone_dict[app_entry.identifier] = Helpers.format_phone_number(app_entry.customer_phone)
            app_identifier_address_dict[app_entry.identifier] = app_entry.customer_address
            app_identifier_city_dict[app_entry.identifier] = app_entry.customer_city
            app_identifier_state_dict[app_entry.identifier] = app_entry.customer_state
            app_identifier_postal_dict[app_entry.identifier] = app_entry.customer_postal

    pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.field_application_identifier.IN(app_ids_to_query))
    for pp_sub in pp_subs:
        info = json.loads(pp_sub.extra_info)
        if "project_management_checkoffs" in info.keys():
            if "received_pto" in info["project_management_checkoffs"].keys():
                if "checked" in info["project_management_checkoffs"]["received_pto"].keys():
                    if info["project_management_checkoffs"]["received_pto"]["checked"]:
                        if "date" in info["project_management_checkoffs"]["received_pto"].keys():
                            dt_vals = info["project_management_checkoffs"]["received_pto"]["date"].split("-")
                            dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))

                            if dt >= start_dt and dt <= end_dt:
                                obj = {}
                                obj["name"] = app_identifier_name_dict[pp_sub.field_application_identifier]
                                obj["pto_date"] = info["project_management_checkoffs"]["received_pto"]["date"]
                                obj["phone"] = app_identifier_phone_dict[pp_sub.field_application_identifier]
                                obj["address"] = app_identifier_address_dict[pp_sub.field_application_identifier]
                                obj["city"] = app_identifier_city_dict[pp_sub.field_application_identifier]
                                obj["state"] = app_identifier_state_dict[pp_sub.field_application_identifier]
                                obj["postal"] = app_identifier_postal_dict[pp_sub.field_application_identifier]

                                customers.append(obj)

                            elif dt >= six_months_ago:
                                obj = {}
                                obj["name"] = app_identifier_name_dict[pp_sub.field_application_identifier]
                                obj["pto_date"] = info["project_management_checkoffs"]["received_pto"]["date"]
                                obj["phone"] = app_identifier_phone_dict[pp_sub.field_application_identifier]
                                obj["address"] = app_identifier_address_dict[pp_sub.field_application_identifier]
                                obj["city"] = app_identifier_city_dict[pp_sub.field_application_identifier]
                                obj["state"] = app_identifier_state_dict[pp_sub.field_application_identifier]
                                obj["postal"] = app_identifier_postal_dict[pp_sub.field_application_identifier]

                                six_months_ago_customers.append(obj)

    for item in six_months_ago_customers:
        s_keys = item.keys()
        for s_key in s_keys:
            item[s_key] = item[s_key].replace(u'\xa0', ' ')



    if len(customers) > 0:
        headers = ('Name', 'Phone', 'Address', 'City', 'State', 'Postal', 'PTO Received')
        headers2 = ('Name', 'Phone', 'Address', 'City', 'State', 'Postal', 'PTO Received')
        data = []
        data2 = []

        for item in customers:
            s_keys = item.keys()
            for s_key in s_keys:
                item[s_key] = item[s_key].replace(u'\xa0', ' ')

        for item in customers:
            data.append(
                    (item["name"], item["phone"], item["address"], item["city"], item["state"], item["postal"], item["pto_date"])
                )

        for item in six_months_ago_customers:
            data2.append(
                    (item["name"], item["phone"], item["address"], item["city"], item["state"], item["postal"], item["pto_date"])
                )

        structured_data = tablib.Dataset(*data, headers=headers)
        attachment_data = {}
        attachment_data["data"] = [base64.b64encode(structured_data.csv)]
        attachment_data["content_types"] = ["text/csv"]
        attachment_data["filenames"] = ["pto_received_customers_" + month_mapping[start_dt.month] + "_" + str(start_dt.year) + ".csv"]

        if len(six_months_ago_customers) > 0:
            structured_data2 = tablib.Dataset(*data2, headers=headers2)
            attachment_data["data"].append(base64.b64encode(structured_data2.csv))
            attachment_data["content_types"].append("text/csv")
            attachment_data["filenames"].append("pto_received_customers_within_last_six_months.csv")

        notification = Notification.first(Notification.action_name == "Monthly PTO Report")
        if not notification is None:
            subject = "PTO Received Customers - " + month_mapping[start_dt.month] + " " + str(start_dt.year)
            msg = "Your report is attached..."
            for p in notification.notification_list:
                Helpers.send_email(p.email_address, subject, msg, attachment_data)

