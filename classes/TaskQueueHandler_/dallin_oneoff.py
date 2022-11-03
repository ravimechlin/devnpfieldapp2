def dallin_oneoff(self):
    app_ids_to_query = ["-1"]
    ret = []
    leads = Lead.query(Lead.rep_identifier == "fff4eb8e26f78c8fc8ec1ca092dc94061f9b470e058cf91a3e0db3d902accb45c17b8744669a6ab2ce20e6bd9d0ea591ef2b6fbcf64c19bb0d02c86fba8da828")
    for lead in leads:
        if lead.dt_accepted.year == 2020:
            app_ids_to_query.append(lead.field_app_identifier)

    ret = []
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
    for app_entry in app_entries:
        obj = {}
        #ak column
        #cd column
        obj["name"] = app_entry.customer_first_name.strip().title()
        obj["phone"] = Helpers.format_phone_number(app_entry.customer_phone)
        obj["email"] = app_entry.customer_email
        obj["address"] = app_entry.customer_address
        obj["city"] = app_entry.customer_city
        obj["state"] = app_entry.customer_state
        obj["postal"] = app_entry.customer_postal
        obj["CD"] = app_entry.deal_closed
        
        stat = LeaderBoardStat.first(
            ndb.AND(
                LeaderBoardStat.metric_key == "appointments_kept",
                LeaderBoardStat.field_app_identifier == app_entry.identifier
            )
        )
        obj["AK"] = not (stat is None)
        ret.append(obj)

    f = GCSLockedFile("/Temp/Dallin/data/json")
    f.write(json.dumps(ret), "application/json", "public-read")
    f.unlock()
