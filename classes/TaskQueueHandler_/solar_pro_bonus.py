def solar_pro_bonus(self):
    from datetime import date
    from datetime import datetime
    from datetime import timedelta

    rep_id_identifier_dict = {}
    rep_identifier_rep_id_dict = {}
    reps = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.current_status == 0,
            FieldApplicationUser.user_type.IN(["solar_pro", "solar_pro_manager"])
        )
    )

    for rep in reps:
        rep_id_identifier_dict[rep.rep_id] = rep.identifier
        rep_identifier_rep_id_dict[rep.identifier] = rep.rep_id

    keys = rep_identifier_rep_id_dict.keys()
    if len(keys) > 0:
        h_p_t = Helpers.pacific_today()
        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        start_dt = start_dt + timedelta(days=-7)
        end_dt = end_dt + timedelta(days=-7)
        
        rep_id_transactions_dict = {}
        stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= end_dt
            )
        )     
        app_ids_to_query = ["-1"]
        field_app_identifier_rep_id_dict = {}
        for stat in stats:
            if stat.rep_id in rep_id_identifier_dict.keys() and stat.metric_key == "appointments_kept" and stat.dt >= datetime(2018, 2, 12):
                app_ids_to_query.append(stat.field_app_identifier)
                field_app_identifier_rep_id_dict[stat.field_app_identifier] = stat.rep_id
                rep_id = stat.rep_id
                if not rep_id in rep_id_transactions_dict.keys():
                    rep_id_transactions_dict[rep_id] = []
                rep_id_transactions_dict[rep_id].append({"recipient": rep_id_identifier_dict[rep_id], "field_app_identifier": stat.field_app_identifier, "name": ""})

        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        app_entry_identifier_name_dict = {}
        for app_entry in app_entries:
            app_entry_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()

        from google.appengine.api import search
        docs_to_put = []
        transactions_to_put = []

        p_date = Helpers.pacific_now()
        while not p_date.isoweekday() == 5:
            p_date = p_date + timedelta(days=1)

        for rep_id in rep_id_transactions_dict.keys():
            for item in rep_id_transactions_dict[rep_id]:
                item["name"] = app_entry_identifier_name_dict[item["field_app_identifier"]]
                v2_transaction = MonetaryTransactionV2(
                    approved=True,
                    cents=0,
                    check_number=-1,
                    created=Helpers.pacific_now(),
                    denied=False,
                    description="Solar Pro AK bonus for " + item["name"],
                    description_key="solar_pro_ak_bonus",
                    dollars=77,
                    extra_info="{}",
                    field_app_identifier=item["field_app_identifier"],
                    identifier=Helpers.guid(),
                    paid=False,
                    payout_date=p_date.date(),
                    recipient=rep_id_identifier_dict[rep_id]
                )
                transactions_to_put.append(v2_transaction)

                docs_to_put.append(
                    search.Document(
                        fields=[
                            search.TextField(name="identifier", value=v2_transaction.identifier),
                            search.TextField(name="description", value=v2_transaction.description)
                        ]
                    )
                )

        if len(transactions_to_put) > 0:
            ndb.put_multi(transactions_to_put)
        if len(docs_to_put) > 0:
            transaction_index = search.Index(name="v2_transactions")
            transaction_index.put(docs_to_put)

