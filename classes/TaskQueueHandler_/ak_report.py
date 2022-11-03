def ak_report(self):
    import tablib
    from datetime import datetime
    rep = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not rep is None:
        aks = LeaderBoardStat.query(LeaderBoardStat.metric_key == "appointments_kept")

        app_ids_to_query = ["-1"]
        for ak in aks:
            if not ak.field_app_identifier == "-1":
                app_ids_to_query.append(ak.field_app_identifier)

        customers = []
        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        for app_entry in app_entries:
            if app_entry.rep_id == rep.rep_id:
                try:
                    obj = {"name": str(app_entry.customer_first_name.strip().title()) + " " + str(app_entry.customer_last_name.strip().title())}
                except:
                    obj = {"name": ""}
                    Helpers.send_email("rnirnber@gmail.com", "bad id 3", app_entry.identifier)
                obj["SP2 Date"] = app_entry.sp_two_time.strftime("%m/%d/%Y %I:%M %P")
                customers.append(obj)

        headers = ('Name', 'SP2')
        data = []
        for item in customers:
            data.append((item["name"],
                item["SP2 Date"]))

        structured_data = tablib.Dataset(*data, headers=headers)
        attachment_data = {}
        attachment_data["data"] = [base64.b64encode(structured_data.csv)]
        attachment_data["content_types"] = ["text/csv"]
        attachment_data["filenames"] = [rep.first_name.strip().lower().replace(" ", "_") + "__" + rep.last_name.strip().lower().replace(" ", "_") + "_aks.csv"]

        Helpers.send_email(self.request.get("email"), "Your AK Report", "See attached....", attachment_data)


