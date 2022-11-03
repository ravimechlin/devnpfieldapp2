def twenty_twenty_report_one(self):
    from datetime import datetime
    import json

    year = int(self.request.get("year"))

    start_dt = None
    end_dt = None

    if self.request.get("month") == "1":
        start_dt = datetime(year, 1, 1, 0, 0, 0)
        end_dt = datetime(year, 1, 31, 23, 59, 59)
    elif self.request.get("month") == "2":
        start_dt = datetime(year, 2, 1, 0, 0, 0)
        end_dt = datetime(year, 2, 28, 23, 59 ,59)
        if year == 2020:
            end_dt = datetime(year, 2, 29, 23, 59, 59)
    elif self.request.get("month") == "3":
        start_dt = datetime(year, 3, 1, 0, 0, 0)
        end_dt = datetime(year, 3, 31, 23, 59, 59)
    elif self.request.get("month") == "4":
        start_dt = datetime(year, 4, 1, 1, 0, 0, 0)
        end_dt = datetime(year, 4, 30, 23, 59, 59)
    elif self.request.get("month") == "5":
        start_dt = datetime(year, 5, 1, 0, 0, 0)
        end_dt = datetime(year, 5, 31, 23, 59, 59)
    elif self.request.get("month") == "6":
        start_dt = datetime(year, 6, 1, 0, 0, 0)
        end_dt = datetime(year, 6, 30, 23, 59, 59)
    elif self.request.get("month") == "7":
        start_dt = datetime(year, 7, 1, 0, 0, 0)
        end_dt = datetime(year, 7, 31, 23, 59, 59)
    elif self.request.get("month") == "8":
        start_dt = datetime(year, 8, 1, 0, 0, 0)
        end_dt = datetime(year, 8, 31, 23, 59, 59)
    elif self.request.get("month") == "9":
        start_dt = datetime(year, 9, 1, 0, 0, 0)
        end_dt = datetime(year, 9, 30, 23, 59, 59)
    elif self.request.get("month") == "10":
        start_dt = datetime(year, 10, 1, 0, 0, 0)
        end_dt = datetime(year, 10, 31, 23, 59, 59)
    elif self.request.get("month") == "11":
        start_dt = datetime(year, 11, 1, 0, 0, 0)
        end_dt = datetime(year, 11, 30, 23, 59, 59)
    elif self.request.get("month") == "12":
        start_dt = datetime(year, 12, 1, 0, 0, 0)
        end_dt = datetime(year, 12, 31, 23, 59, 59)

    field_app_identifier_date_dict = {}
    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= start_dt,
            LeaderBoardStat.dt <= end_dt,
            LeaderBoardStat.metric_key == "leads_acquired"
        )
    )

    cust_ids_to_query = ["-1"]
    for stat in stats:
        cust_ids_to_query.append(stat.field_app_identifier)
        field_app_identifier_date_dict[stat.field_app_identifier] = str(stat.dt.date())

    customers = []
    customerss = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(cust_ids_to_query))
    for c in customerss:
        customers.append(c)




    data = []
    sp_ids_to_query = ["-1"]

    sp_identifier_name_dict = {}
    sp_identifier_name_dict["-1"] = "N/A"

    rep_ids_to_query = ["-1"]
    rep_identifier_name_dict = {"-1": "Error"}

    email_sent = False

    for customer in customers:
        obj = {}
        obj["first_name"] = customer.customer_first_name.strip().title()
        obj["last_name"] = customer.customer_last_name.strip().title()
        obj["street_address"] = customer.customer_address.strip().title()
        obj["city"] = customer.customer_city.strip().title()
        obj["state"] = customer.customer_state.upper()
        obj["postal"] = customer.customer_postal
        obj["email"] = customer.customer_email
        obj["phone"] = Helpers.format_phone_number(customer.customer_phone)
        obj["date_entered"] = field_app_identifier_date_dict[customer.identifier]
        obj["rep_name"] = "Error"
        obj["token"] = customer.identifier
        obj["solar_pro_token"] = "-1"
        obj["rep_id"] = customer.rep_id
        obj["utc_timestamp"] = customer.insert_time
        obj["solar_pro_name"] = "N/A"

        if not customer.lead_generator == "-1":
            if not customer.lead_generator in sp_ids_to_query:
                sp_ids_to_query.append(customer.lead_generator)
            obj["solar_pro_token"] = customer.lead_generator

        if not customer.rep_id in rep_ids_to_query:
            rep_ids_to_query.append(customer.rep_id)

        data.append(obj)

    solar_pros = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(sp_ids_to_query))
    for sp in solar_pros:
        sp_identifier_name_dict[sp.identifier] = sp.first_name.strip().title() + " " + sp.last_name.strip().title()

    reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))
    for rep in reps:
        if not rep.rep_id in rep_identifier_name_dict.keys():
                rep_identifier_name_dict[rep.rep_id] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

    for obj in data:
        if obj["solar_pro_token"] in sp_identifier_name_dict.keys():
            obj["solar_pro_name"] = sp_identifier_name_dict[obj["solar_pro_token"]]
        if obj["rep_id"] in rep_identifier_name_dict.keys():
            obj["rep_name"] = rep_identifier_name_dict[obj["rep_id"]]

        #obj["date"] = Helpers.epoch_millis_to_pacific_dict(obj["utc_timestamp"])

    f = GCSLockedFile("/Reports/" + self.request.get("year") + "/" + self.request.get("month") + "_report_one.json")
    f.write(json.dumps(data), "application/json", "public-read")
    f.unlock()
