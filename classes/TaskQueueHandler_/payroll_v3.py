def payroll_v3(self):
    import json

    from datetime import datetime
    from datetime import timedelta
    from google.appengine.api import search

    docs_to_put = []
    s_index = search.Index(name="v2_transactions")
    
    if self.request.get("fn") == "solar_pro_hks":
        h_p_t = Helpers.pacific_today()
        h_p_n = Helpers.pacific_now()

        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        start_dt = start_dt + timedelta(days=-7)
        end_dt = end_dt + timedelta(days=-7)

        #hks = LeaderBoardStat.query(
        #    ndb.AND(
        #        LeaderBoardStat.dt >= start_dt,
        #        LeaderBoardStat.dt <= end_dt,
        #        LeaderBoardStat.metric_key == "hours_knocked_v2"
        #    )
        #)
        hks = HKTally.query(
            ndb.AND(
                HKTally.dt >= start_dt,
                HKTally.dt <= end_dt
            )
        )
        rep_ids_to_query = ["-1"]
        rep_id_tally_dict = {}
        rep_identifier_tally_dict = {}

        for hk in hks:
            if not hk.rep_identifier in rep_identifier_tally_dict.keys():
                rep_identifier_tally_dict[hk.rep_identifier] = 0

            rep_identifier_tally_dict[hk.rep_identifier] += hk.minutes
            if not hk.rep_identifier in rep_ids_to_query:
                rep_ids_to_query.append(hk.rep_identifier)

        for rep_identifier in rep_identifier_tally_dict.keys():
            minutes = rep_identifier_tally_dict[rep_identifier]
            hours = float(minutes) / float(60)
            hours = round(hours, 0)
            hours = int(hours)
            rep_identifier_tally_dict[rep_identifier] = hours

        rep_identifier_tally_dict2 = {}
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
        rep_id_office_id_dict = {}
        offices_to_query = ["-1"]
        rep_id_rep_identifier_dict = {}
        rep_id_manager_dict = {}
        rep_identifier_manager_dict = {}
        rep_identifier_rep_id_dict = {}
        for rep in reps:
            rep_id_rep_identifier_dict[rep.rep_id] = rep.identifier
            rep_identifier_rep_id_dict[rep.identifier] = rep.rep_id
            if rep.user_type == "solar_pro" or rep.user_type == "solar_pro_manager":
                rep_identifier_tally_dict2[rep.identifier] = rep_identifier_tally_dict[rep.identifier]

                if not rep.main_office in offices_to_query:
                    offices_to_query.append(rep.main_office)
                
                rep_id_office_id_dict[rep.rep_id] = rep.main_office

            rep_id_manager_dict[rep.rep_id] = rep.user_type == "solar_pro_manager"
            rep_identifier_manager_dict[rep.identifier] = rep.user_type == "solar_pro_manager"

        office_identifier_parent_identifier_dict = {}
        offices = OfficeLocation.query(OfficeLocation.identifier.IN(offices_to_query))
        for office in offices:
            office_identifier_parent_identifier_dict[office.identifier] = office.parent_identifier


        pricing_structures = Helpers.get_pricing_structures()
        transactions = []
        
        this_upcoming_friday = Helpers.pacific_now()
        while not this_upcoming_friday.isoweekday() == 5:
            this_upcoming_friday = this_upcoming_friday + timedelta(days=1)
        this_upcoming_friday = this_upcoming_friday.date()

        kv_keys_to_query = []
        for rep_identifier in rep_identifier_tally_dict2.keys():
            kv_keys_to_query.append("pay_per_hk_" + rep_identifier)


        compensation_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(kv_keys_to_query))
        rep_identifier_compensation_dict = {}
        for compensation_kv in compensation_kvs:
            rep_identifier_compensation_dict[compensation_kv.keyy.replace("pay_per_hk_", "")] = compensation_kv.val

        for rep_identifier in rep_identifier_tally_dict2.keys():
            rep_id = rep_identifier_rep_id_dict[rep_identifier]
            office_identifier = rep_id_office_id_dict[rep_id]
            market_key = office_identifier_parent_identifier_dict[office_identifier]

            if market_key in pricing_structures.keys():
                if "solar_pro_pay_per_hk" in pricing_structures[market_key].keys():
                    pay_per_hk = float(pricing_structures[market_key]["solar_pro_pay_per_hk"].replace("$", "").replace(",", ""))

                    if rep_identifier_manager_dict[rep_identifier]:
                        if "solar_pro_manager_pay_per_hk" in pricing_structures[market_key].keys():
                            pay_per_hk = float(pricing_structures[market_key]["solar_pro_manager_pay_per_hk"].replace("$", "").replace(",", ""))

                    if rep_identifier in rep_identifier_compensation_dict.keys():
                        pay_per_hk = float(rep_identifier_compensation_dict[rep_identifier].replace("$", "").replace(",", ""))

                    total_hks = float(rep_identifier_tally_dict2[rep_identifier])
                    total = pay_per_hk * total_hks
                    dollarss = int(total)
                    centss = total - dollarss
                    centss *= 100
                    centss = int(centss)
                    descrip = "HK pay for period " + str(start_dt.date()) + " --- " + str(end_dt.date()) + ": " + str(total_hks) + " @ " + Helpers.currency_format(pay_per_hk) + " per HK = " + Helpers.currency_format(total) + "."

                    if dollarss > 0 or centss > 0:
                        transaction = MonetaryTransactionV2(
                            approved=True,
                            cents=centss,
                            check_number=-1,
                            created=h_p_n,
                            denied=False,
                            description=descrip,
                            description_key="solar_pro_hk_pay",
                            dollars=dollarss,
                            extra_info="{}",
                            field_app_identifier="-1",
                            identifier=Helpers.guid(),
                            paid=False,
                            payout_date=this_upcoming_friday,
                            recipient=rep_identifier
                        )
                        transactions.append(transaction)

                        docs_to_put.append(
                            search.Document(
                                fields=[
                                    search.TextField(name="identifier", value=transaction.identifier),
                                    search.TextField(name="description", value=transaction.description)
                                ]
                            )
                        )

        if len(transactions) > 1:
            ndb.put_multi(transactions)
        elif len(transactions) == 1:
            transactions[0].put()

    elif self.request.get("fn") == "solar_pro_ak_pay":
        h_p_t = Helpers.pacific_today()
        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        start_dt = start_dt + timedelta(days=-7)
        end_dt = end_dt + timedelta(days=-7)

        eligible_users = FieldApplicationUser.query(FieldApplicationUser.user_type.IN(["solar_pro", "solar_pro_manager"]))
        user_identifier_name_dict = {}
        user_identifier_user_type_dict = {}
        user_identifier_rep_id_dict = {}
        rep_id_user_identifier_dict = {}
        user_identifier_office_dict = {}
        office_ids_to_query = ["-1"]
        eligible_rep_ids = []
        for user in eligible_users:
            user_identifier_name_dict[user.identifier] = user.first_name.strip().title() + " " + user.last_name.strip().title()
            user_identifier_user_type_dict[user.identifier] = user.user_type
            user_identifier_rep_id_dict[user.identifier] = user.rep_id
            user_identifier_office_dict[user.identifier] = user.main_office
            rep_id_user_identifier_dict[user.rep_id] = user.identifier
            if not user.main_office in office_ids_to_query:
                office_ids_to_query.append(user.main_office)
            eligible_rep_ids.append(user.rep_id)

        office_identifier_market_dict = {}
        offices = OfficeLocation.query(OfficeLocation.identifier.IN(office_ids_to_query))
        for office in offices:
            office_identifier_market_dict[office.identifier] = office.parent_identifier

        stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "appointments_kept",
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= end_dt
            )
        )

        proto_transactions = []
        app_identifier_idx_dict = {}
        app_identifier_recorded_dt_dict = {}
        app_ids_to_query = ["-1"]
        kv_keys_to_query = ["-1"]
        kv_keys_to_query2 = ["-1"]
        for stat in stats:
            if stat.rep_id in eligible_rep_ids:
                app_identifier_idx_dict[stat.field_app_identifier] = len(proto_transactions)
                app_identifier_recorded_dt_dict[stat.field_app_identifier] = str(stat.dt.date())
                obj = {"field_app_identifier": stat.field_app_identifier}
                obj["rep_id"] = stat.rep_id
                obj["usage_type"] = "estimated"
                obj["dollars"] = 0
                obj["cents"] = 0
                obj["amigo"] = False
                proto_transactions.append(obj)
                app_ids_to_query.append(obj["field_app_identifier"])
                kv_keys_to_query.append("original_real_or_estimated_" + stat.field_app_identifier)
                kv_keys_to_query2.append("ab_override_" + stat.field_app_identifier)

        stats2 = LeaderBoardStat.query(ndb.AND(
            LeaderBoardStat.field_app_identifier.IN(app_ids_to_query),
            LeaderBoardStat.metric_key == "leads_acquired_amigo"
        ))

        for stat in stats2:
            idx = app_identifier_idx_dict[stat.field_app_identifier]
            proto_transactions[idx]["amigo"] = True

        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        app_identifier_name_dict = {}
        app_identifier_sp2_dict = {}
        for app_entry in app_entries:
            app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
            app_identifier_sp2_dict[app_entry.identifier] = str(app_entry.sp_two_time.date())

        kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(kv_keys_to_query))
        for kv in kvs:
            app_identifier = kv.keyy.split("_")[4]
            idx = app_identifier_idx_dict[app_identifier]
            if kv.val == "real":
                proto_transactions[idx]["usage_type"] = "real"

        override_identifiers = []
        kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(kv_keys_to_query2))
        for kv in kvs:
            override_identifiers.append(kv.keyy.replace("ab_override_", ""))

        pricing_structures = Helpers.get_pricing_structures()
        for proto in proto_transactions:
            rep_identifier = rep_id_user_identifier_dict[proto["rep_id"]]
            office_identifier = user_identifier_office_dict[rep_identifier]
            market_key = office_identifier_market_dict[office_identifier]
            user_type = user_identifier_user_type_dict[rep_identifier]
            proto["rep_identifier"] = rep_identifier
            amount = float(0)
            if market_key in pricing_structures.keys():
                base_pay_key = user_type + "_pay_per_ak"
                bonus_key = user_type + "_real_usage_ak_bonus"

                base_amount = float(0)
                if base_pay_key in pricing_structures[market_key].keys():
                    base_amount = pricing_structures[market_key][base_pay_key]
                    base_amount = base_amount.replace("$", "").replace(",", "")
                    base_amount = float(base_amount)
                bonus_amount = float(0)
                if proto["usage_type"] == "real":
                    if bonus_key in pricing_structures[market_key].keys():
                        bonus_amount = pricing_structures[market_key][bonus_key]
                        bonus_amount = bonus_amount.replace("$", "").replace(",", "")
                        bonus_amount = float(bonus_amount)

                the_sum = base_amount + bonus_amount

                if proto["amigo"]:
                    the_sum += float(100)

                the_sum = round(the_sum, 2)
                proto["dollars"] = int(the_sum)
                the_sum -= float(int(proto["dollars"]))
                cents = the_sum * float(100)
                cents = int(cents)
                proto["cents"] = cents
                proto["description"] = "AK pay for " + app_identifier_name_dict[proto["field_app_identifier"]] + " with " + proto["usage_type"] + " usage data obtained."
                if proto["amigo"]:
                    proto["description"] += " This was a friends/family deal."
                proto["description"] += " AK Recorded: "
                proto["description"] += app_identifier_recorded_dt_dict[proto["field_app_identifier"]]
                proto["description"] + "."
                proto["description"] += " SP2 Date: "
                proto["description"] += app_identifier_sp2_dict[proto["field_app_identifier"]]
                proto["description"] += "."

        payout_dt = Helpers.pacific_now()
        while not payout_dt.isoweekday() == 5:
            payout_dt = payout_dt + timedelta(days=1)

        h_p_n = Helpers.pacific_now()
        transactions = []
        
        notes = CustomerNote.query(
            ndb.AND(
                CustomerNote.field_app_identifier.IN(app_ids_to_query),
                CustomerNote.note_key == "welfare"
            )
        )

        welfare_app_ids = []

        for note in notes:
            welfare_app_ids.append(note.field_app_identifier)
        
        for proto in proto_transactions:
            transaction = MonetaryTransactionV2(
                approved=True,
                cents=proto["cents"],
                check_number=-1,
                created=h_p_n,
                denied=False,
                description=proto["description"],
                description_key="ak_pay",
                dollars=proto["dollars"],
                extra_info="{}",
                field_app_identifier=proto["field_app_identifier"],
                identifier=Helpers.guid(),
                paid=False,
                payout_date=payout_dt.date(),
                recipient=proto["rep_identifier"]
            )
            if proto["field_app_identifier"] in override_identifiers:
                transaction.description = "ALTHOUGH THIS WAS A CARE CUSTOMER, AK PAY SHOULD STILL HAPPEN. " + transaction.description
            elif proto["field_app_identifier"] in welfare_app_ids:
                transaction.description = app_identifier_name_dict[proto["field_app_identifier"]] + " was marked as CARE."
                transaction.dollars = 0
                transaction.cents = 25                

            if transaction.dollars > 0 or transaction.cents > 0:
                if (not proto["field_app_identifier"] in welfare_app_ids) or (proto["field_app_identifier"] in override_identifiers) or (transaction.cents == 25 and transaction.dollars == 0):
                    docs_to_put.append(
                        search.Document(
                            fields=[
                                search.TextField(name="identifier", value=transaction.identifier),
                                search.TextField(name="description", value=transaction.description)
                            ]
                        )
                    )
                    transactions.append(transaction)

        if len(transactions) == 1:
            transactions[0].put()
        elif len(transactions) > 1:
            ndb.put_multi(transactions)

    elif self.request.get("fn") == "legacy_overrides":
        h_p_n = Helpers.pacific_now()

        second_friday_of_month = datetime(h_p_n.year, h_p_n.month, 1)
        friday_count = int(second_friday_of_month.isoweekday() == 5)
        while not friday_count == 2:
            second_friday_of_month = second_friday_of_month + timedelta(days=1)
            friday_count += int(second_friday_of_month.isoweekday() == 5)

        now = Helpers.pacific_now()
        one_year_ago = now + timedelta(days=-365)
        last_month_start = now
        last_month_end = None
        month_change = False
        while not month_change:
            current_month = last_month_start.month
            last_month_start = last_month_start + timedelta(days=-1)
            month_after_subtract = last_month_start.month

            month_change = not (current_month == month_after_subtract)
            if month_change:
                last_month_start_cpy = datetime(last_month_start.year, last_month_start.month, last_month_start.day)
                last_month_start = datetime(last_month_start.year, last_month_start.month, 1)
                last_month_end = datetime(last_month_start_cpy.year, last_month_start_cpy.month, last_month_start_cpy.day, 23, 59, 59)

        rep_ids_to_query = ["-1"]
        app_ids_to_query = ["-1"]
        booking_ids_to_query = ["-1"]
        pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.rep_submission_date >= one_year_ago)
        keepers = []
        for pp_sub in pp_subs:
            info = json.loads(pp_sub.extra_info)
            if "project_management_checkoffs" in info.keys():
                if "install" in info["project_management_checkoffs"].keys():
                    if "checked" in info["project_management_checkoffs"]["install"].keys():
                        if info["project_management_checkoffs"]["install"]["checked"]:
                            if "date" in info["project_management_checkoffs"]["install"].keys():
                                dt_vals = info["project_management_checkoffs"]["install"]["date"].split("-")
                                dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                         
                                if (dt >= last_month_start) and (dt <= last_month_end):
                                    keepers.append(pp_sub)
                                    rep_ids_to_query.append(pp_sub.rep_identifier)
                                    app_ids_to_query.append(pp_sub.field_application_identifier)

        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
        rep_identifier_name_dict = {}
        rep_identifier_rep_id_dict = {}
        rep_id_rep_identifier_dict = {}
        rep_identifier_office_dict = {}
        for rep in reps:
            rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
            rep_identifier_rep_id_dict[rep.identifier] = rep.rep_id
            rep_id_rep_identifier_dict[rep.rep_id] = rep.identifier
            rep_identifier_office_dict[rep.identifier] = rep.main_office

        app_identifier_booking_dict = {}
        bookings = SurveyBooking.query(SurveyBooking.field_app_identifier.IN(app_ids_to_query))
        for booking in bookings:
            app_identifier_booking_dict[booking.field_app_identifier] = booking

        app_identifier_name_dict = {}
        app_identifier_office_dict = {}
        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        for app_entry in app_entries:
            app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
            app_identifier_office_dict[app_entry.identifier] = app_entry.office_identifier

        app_identifier_proposals_dict = {}
        proposals = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(app_ids_to_query))
        for proposal in proposals:
            app_identifier_proposals_dict[proposal.field_app_identifier] = proposal

        
        office_locations = OfficeLocation.query(OfficeLocation.is_parent == False)
        office_identifier_override_data_dict = {}
        office_identifier_market_dict = {}
        for o_location in office_locations:
            office_identifier_override_data_dict[o_location.identifier] = o_location.get_override_data()
            office_identifier_market_dict[o_location.identifier] = o_location.parent_identifier

        pricing_structures = Helpers.get_pricing_structures()

        transactions = []

        for keeper in keepers:
            rep_identifier = keeper.rep_identifier
            office_identifier = rep_identifier_office_dict[rep_identifier]
            override_data = office_identifier_override_data_dict[office_identifier]
            if rep_identifier in override_data["yielders"]:
                if rep_identifier in override_data["data"].keys():
                    for item in override_data["data"][rep_identifier]:
                        if float(item["amount"]) > float(0):
                            office_identifier = app_identifier_office_dict[keeper.field_application_identifier]
                            market_identifier = office_identifier_market_dict[office_identifier]
                            booking = app_identifier_booking_dict[keeper.field_application_identifier]
                            fund_name_components = booking.fund.split("_")
                            proposal = app_identifier_proposals_dict[keeper.field_application_identifier]
                            proposal.fix_additional_amount()
                            proposal.fix_system_size()
                            info = json.loads(proposal.info)
                            system_size = float(info["system_size"])


                            multip_factor = 1.0
                            if "lease" in fund_name_components or "ppa" in fund_name_components:
                                if market_identifier in pricing_structures.keys():
                                    if "ppa_override_multiplication_factor" in pricing_structures[market_identifier].keys():
                                        multip_factor = float(pricing_structures[market_identifier]["ppa_override_multiplication_factor"])

                            gross = multip_factor * float(item["amount"]) * system_size
                            dollarss = int(gross)
                            centss = gross - dollarss
                            centss *= 100
                            centss = int(centss)

                            descrip = "Legacy override for " + rep_identifier_name_dict[keeper.rep_identifier] + " selling a " + str(system_size) + " KW system to " + app_identifier_name_dict[keeper.field_application_identifier] + ". " + str(multip_factor) + " * " + Helpers.currency_format(float(item["amount"])) + " * " + str(system_size) + " = " + Helpers.currency_format(gross) + "."

                            transaction = MonetaryTransactionV2(
                                approved=True,
                                cents=centss,
                                check_number=-1,
                                created=h_p_n,
                                denied=False,
                                description=descrip,
                                description_key="legacy_override",
                                dollars=dollarss,
                                extra_info="{}",
                                field_app_identifier=keeper.field_application_identifier,
                                identifier=Helpers.guid(),
                                paid=False,
                                payout_date=second_friday_of_month,
                                recipient=item["identifier"]
                            )
                            if dollarss > 0 or centss > 0:
                                docs_to_put.append(
                                    search.Document(
                                        fields=[
                                            search.TextField(name="identifier", value=transaction.identifier),
                                            search.TextField(name="description", value=transaction.description)
                                        ]
                                    )
                                )
                                transactions.append(transaction)

        if len(transactions) == 1:
            transactions[0].put()
        elif len(transactions) > 1:
            ndb.put_multi(transactions)

    elif self.request.get("fn") == "solar_pro_commissions":
        h_p_n = Helpers.pacific_now()

        second_friday_of_month = datetime(h_p_n.year, h_p_n.month, 1)
        friday_count = int(second_friday_of_month.isoweekday() == 5)
        while not friday_count == 2:
            second_friday_of_month = second_friday_of_month + timedelta(days=1)
            friday_count += int(second_friday_of_month.isoweekday() == 5)

        now = Helpers.pacific_now()
        one_year_ago = now + timedelta(days=-365)
        last_month_start = now
        last_month_end = None
        month_change = False
        while not month_change:
            current_month = last_month_start.month
            last_month_start = last_month_start + timedelta(days=-1)
            month_after_subtract = last_month_start.month

            month_change = not (current_month == month_after_subtract)
            if month_change:
                last_month_start_cpy = datetime(last_month_start.year, last_month_start.month, last_month_start.day)
                last_month_start = datetime(last_month_start.year, last_month_start.month, 1)
                last_month_end = datetime(last_month_start_cpy.year, last_month_start_cpy.month, last_month_start_cpy.day, 23, 59, 59)

        rep_ids_to_query = ["-1"]
        pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.rep_submission_date >= one_year_ago)
        keepers = []
        for pp_sub in pp_subs:
            info = json.loads(pp_sub.extra_info)
            if "project_management_checkoffs" in info.keys():
                if "install" in info["project_management_checkoffs"].keys():
                    if "checked" in info["project_management_checkoffs"]["install"].keys():
                        if info["project_management_checkoffs"]["install"]["checked"]:
                            if "date" in info["project_management_checkoffs"]["install"].keys():
                                dt_vals = info["project_management_checkoffs"]["install"]["date"].split("-")
                                dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                         
                                if (dt >= last_month_start) and (dt <= last_month_end):
                                    keepers.append(pp_sub)
                                    rep_ids_to_query.append(pp_sub.rep_identifier)

        rep_identifier_name_dict_5 = {}
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
        for rep in reps:
            rep_identifier_name_dict_5[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

        app_ids_to_query = ["-1"]
        for keeper in keepers:
            app_ids_to_query.append(keeper.field_application_identifier)

        kv_keys_to_query1 = ["-1"]
        kv_keys_to_query2 = ["-1"]
        app_identifier_name_dict = {}
        app_identifier_solar_pro_dict = {}
        solar_pro_ids_to_query = ["-1"]

        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        eligible_app_entries = []
        for app_entry in app_entries:
            app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
            if (not app_entry.lead_generator == "-1") and (not app_entry.lead_generator == "n/a"):
                solar_pro_ids_to_query.append(app_entry.lead_generator)
                eligible_app_entries.append(app_entry.identifier)
                app_identifier_solar_pro_dict[app_entry.identifier] = app_entry.lead_generator
                kv_keys_to_query1.append("pay_per_install_" + app_entry.lead_generator)
                kv_keys_to_query2.append("pay_per_install_per_kw_" + app_entry.lead_generator)

        solar_pro_identifier_name_dict = {}
        solar_pro_manager_dict = {}
        office_ids_to_query = ["-1"]
        solar_pro_identifier_office_dict = {}
        solar_pros = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(solar_pro_ids_to_query))
        for solar_pro in solar_pros:
            solar_pro_identifier_name_dict[solar_pro.identifier] = solar_pro.first_name.strip().title() + " " + solar_pro.last_name.strip().title()
            solar_pro_manager_dict[solar_pro.identifier] = (solar_pro.user_type == "solar_pro_manager")
            office_ids_to_query.append(solar_pro.main_office)
            solar_pro_identifier_office_dict[solar_pro.identifier] = solar_pro.main_office

        office_identifier_parent_identifier_dict = {}
        offices = OfficeLocation.query(OfficeLocation.identifier.IN(office_ids_to_query))
        for office in offices:
            office_identifier_parent_identifier_dict[office.identifier] = office.parent_identifier

        pricing_structures = Helpers.get_pricing_structures()
        solar_pro_identifier_compensation_dict = {}

        for solar_pro_identifier in solar_pro_identifier_office_dict.keys():
            base_pay = float(0)
            per_kw_pay = float(0)
            office_identifier = solar_pro_identifier_office_dict[solar_pro_identifier]
            market_key = office_identifier_parent_identifier_dict[office_identifier]

            manager = solar_pro_manager_dict[solar_pro_identifier]
            if market_key in pricing_structures.keys():
                base_pay_key = ["solar_pro_flat_amount_per_install", "solar_pro_manager_flat_amount_per_install"][int(manager)]
                per_kw_key = ["solar_pro_per_kw_amount_per_install", "solar_pro_manager_per_kw_amount_per_install"][int(manager)]

                if base_pay_key in pricing_structures[market_key].keys():
                    base_pay = float(pricing_structures[market_key][base_pay_key].replace("$", "").replace(",", ""))

                if per_kw_key in pricing_structures[market_key].keys():
                    per_kw_pay = float(pricing_structures[market_key][per_kw_key].replace("$", "").replace(",", ""))

            solar_pro_identifier_compensation_dict[solar_pro_identifier] = {"base": base_pay, "kw": per_kw_pay}

        first_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(kv_keys_to_query1))
        for kv in first_kvs:
            solar_pro_identifier = kv.keyy.replace("pay_per_install_", "")
            solar_pro_identifier_compensation_dict[solar_pro_identifier]["base"] = float(kv.val.replace("$", "").replace(",", ""))

        second_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(kv_keys_to_query2))
        for kv in second_kvs:
            solar_pro_identifier = kv.keyy.replace("pay_per_install_per_kw_", "")
            solar_pro_identifier_compensation_dict[solar_pro_identifier]["kw"] = float(kv.val.replace("$", "").replace(",", ""))

        app_ids_to_query = ["-1"]
        keepers2 = []
        for keeper in keepers:
            if keeper.field_application_identifier in eligible_app_entries:
                keepers2.append(keeper)
                app_ids_to_query.append(keeper.field_application_identifier)

        keepers = keepers2

        app_identifier_system_size_dict = {}
        proposals = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(app_ids_to_query))
        for proposal in proposals:
            proposal.fix_additional_amount()
            proposal.fix_system_size()

            app_identifier_system_size_dict[proposal.field_app_identifier] = float(json.loads(proposal.info)["system_size"])

        transactions = []
        for keeper in keepers:
            solar_pro_identifier = app_identifier_solar_pro_dict[keeper.field_application_identifier]

            base = solar_pro_identifier_compensation_dict[solar_pro_identifier]["base"]
            per_kw = solar_pro_identifier_compensation_dict[solar_pro_identifier]["kw"]

            descrip = "Commission for " + rep_identifier_name_dict_5[keeper.rep_identifier] + " selling a " + str(app_identifier_system_size_dict[keeper.field_application_identifier]) + " system to " + app_identifier_name_dict[keeper.field_application_identifier] + "."
            descrip += " A flat amount of " + Helpers.currency_format(base) + " is awarded."
            if per_kw > float(0):
                descrip += " An additional per KW bonus of " + Helpers.currency_format(per_kw) + " is added."
                descrip += " " + str(per_kw) + " * " + str(app_identifier_system_size_dict[keeper.field_application_identifier]) + " = " + Helpers.currency_format(per_kw * app_identifier_system_size_dict[keeper.field_application_identifier]) + "."

            gross = base + (per_kw * app_identifier_system_size_dict[keeper.field_application_identifier])
            dollarss = int(gross)
            centss = gross - dollarss
            centss *= 100
            centss = int(centss)

            transaction = MonetaryTransactionV2(
                approved=True,
                cents=centss,
                check_number=-1,
                created=h_p_n,
                denied=False,
                description=descrip,
                description_key="solar_pro_sales_commission",
                dollars=dollarss,
                extra_info="{}",
                field_app_identifier=keeper.field_application_identifier,
                identifier=Helpers.guid(),
                paid=False,
                payout_date=second_friday_of_month,
                recipient=solar_pro_identifier
            )
            if dollarss > 0 or centss > 0:
                transactions.append(transaction)

                docs_to_put.append(
                    search.Document(
                        fields=[
                            search.TextField(name="identifier", value=transaction.identifier),
                            search.TextField(name="description", value=transaction.description)
                        ]
                    )
                )

        if len(transactions) > 1:
            ndb.put_multi(transactions)
        elif len(transactions) == 1:
            transactions[0].put()

    elif self.request.get("fn") == "issue_ak_payments_to_cares":
        transactions = []
        field_app_identifiers_paid = []
        h_p_t = Helpers.pacific_today()
        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        start_dt = start_dt + timedelta(days=-7)
        end_dt = end_dt + timedelta(days=-7)

        ##
        #start_dt = datetime(2019, 5, 1)
        #end_dt = datetime(2019, 6, 24)

        stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "packets_submitted",
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= end_dt
            )
        )

        app_identifier_cd_date_dict = {}
        app_identifier_rep_id_dict = {}
        cd_app_identifiers = []
        rep_ids_to_query = ["-5"]
        for stat in stats:
            cd_app_identifiers.append(stat.field_app_identifier)
            app_identifier_cd_date_dict[stat.field_app_identifier] = str(stat.dt.date())
            app_identifier_rep_id_dict[stat.field_app_identifier] = stat.rep_id
            rep_ids_to_query.append(stat.rep_id)

        rep_id_name_dict = {}
        reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))
        for rep in reps:
            rep_id_name_dict[rep.rep_id] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
        

        if len(cd_app_identifiers) > 0:
            app_identifier_lead_generator_dict = {}

            eligible_app_identifiers = []
            app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(cd_app_identifiers))
            app_identifier_name_dict = {}
            for app_entry in app_entries:
                app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
                if not app_entry.lead_generator == "-1":
                    app_identifier_lead_generator_dict[app_entry.identifier] = app_entry.lead_generator
                    eligible_app_identifiers.append(app_entry.identifier)

            if len(eligible_app_identifiers) > 0:
                existing_transactions = MonetaryTransactionV2.query(
                    ndb.AND(
                        MonetaryTransactionV2.field_app_identifier.IN(eligible_app_identifiers),
                        MonetaryTransactionV2.description_key == "ak_pay"
                    )                                        
                )

                data = []
                already_paid_aks = []
                aks_to_pay = []
                loop_count = 0
                for et in existing_transactions:
                    loop_count += 1
                    already_paid = True
                    if et.dollars == 0 and et.cents == 25:
                        already_paid = False
                    if already_paid:
                        already_paid_aks.append(et.field_app_identifier)
                    else:
                        aks_to_pay.append(et.field_app_identifier)

                payout_dt = Helpers.pacific_now()
                while not payout_dt.isoweekday() == 5:
                    payout_dt = payout_dt + timedelta(days=1)

                

                pricing_structures = Helpers.get_pricing_structures()
                proto_transactions = []
                for app_identifier in eligible_app_identifiers:
                    if not app_identifier in already_paid_aks:
                        usage_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "original_real_or_estimated_" + app_identifier)
                        if not usage_kv is None:                            
                            rep_id = app_identifier_rep_id_dict[app_identifier]
                            rep_name = rep_id_name_dict[rep_id]
                            obj = {}
                            obj["field_app_identifier"] = app_identifier
                            obj["description"] = "AK Pay for " + rep_name + " closing " + app_identifier_name_dict[app_identifier] + "'s deal on " + app_identifier_cd_date_dict[app_identifier] + "."
                            amigo_stat = LeaderBoardStat.first(
                                ndb.AND(
                                    LeaderBoardStat.field_app_identifier == app_identifier,
                                    LeaderBoardStat.metric_key == "leads_acquired_amigo"
                                )
                            )
                            obj["amigo"] = (not amigo_stat is None)
                            obj["dollars"] = 0
                            obj["cents"] = 0
                            obj["recipient"] = app_identifier_lead_generator_dict[app_identifier]
                            obj["usage_type"] = usage_kv.val
                            obj["description"] += " Original usage data obtained was " + obj["usage_type"] + "."
                            obj["payout"] = str(payout_dt)

                            sp = FieldApplicationUser.first(FieldApplicationUser.identifier == app_identifier_lead_generator_dict[app_identifier])
                            if not sp is None:
                                office = OfficeLocation.first(OfficeLocation.identifier == sp.main_office)
                                if not office is None:
                                    market_key = office.parent_identifier
                                    user_type = sp.user_type

                                    amount = float(0)
                                    base_pay_key = user_type + "_pay_per_ak"
                                    bonus_key = user_type + "_real_usage_ak_bonus"
                                    base_amount = float(0)

                                    if base_pay_key in pricing_structures[market_key].keys():
                                        base_amount = pricing_structures[market_key][base_pay_key]
                                        base_amount = base_amount.replace("$", "").replace(",", "")
                                        base_amount = float(base_amount)

                                    bonus_amount = float(0)
                                    if obj["usage_type"] == "real":
                                        if bonus_key in pricing_structures[market_key].keys():
                                            bonus_amount = pricing_structures[market_key][bonus_key]
                                            bonus_amount = bonus_amount.replace("$", "").replace(",", "")
                                            bonus_amount = float(bonus_amount)

                                    the_sum = base_amount + bonus_amount
                                    if obj["amigo"]:
                                        the_sum += float(100)

                                    the_sum = round(the_sum, 2)
                                    obj["dollars"] = int(the_sum)
                                    the_sum -= float(int(obj["dollars"]))
                                    cents = the_sum * float(100)
                                    cents = int(cents)
                                    obj["cents"] = cents

                                    proto_transactions.append(obj)

                                    

                h_p_n = Helpers.pacific_now()
                for transaction in proto_transactions:
                    t2 = MonetaryTransactionV2(
                        approved=True,
                        cents=transaction["cents"],
                        check_number=-1,
                        created=h_p_n,
                        denied=False,
                        description=transaction["description"],
                        description_key="ak_pay",
                        dollars=transaction["dollars"],
                        extra_info="{}",
                        field_app_identifier=transaction["field_app_identifier"],
                        identifier=Helpers.guid(),
                        paid=False,
                        payout_date=payout_dt.date(),
                        recipient=transaction["recipient"]
                    )                    

                    if t2.dollars > 0 or t2.cents > 0:
                        if not t2.field_app_identifier in field_app_identifiers_paid:
                            field_app_identifiers_paid.append(t2.field_app_identifier)
                            docs_to_put.append(
                                search.Document(
                                    fields=[
                                        search.TextField(name="identifier", value=t2.identifier),
                                        search.TextField(name="description", value=t2.description)
                                    ]
                                )
                            )
                            transactions.append(t2)                        

        if len(transactions) == 1:
            transactions[0].put()
        elif len(transactions) > 1:
            ndb.put_multi(transactions)


    elif self.request.get("fn") == "solar_pro_manager_overrides":
        transactions = []
        h_p_n = Helpers.pacific_now()

        second_friday_of_month = datetime(h_p_n.year, h_p_n.month, 1)
        friday_count = int(second_friday_of_month.isoweekday() == 5)
        while not friday_count == 2:
            second_friday_of_month = second_friday_of_month + timedelta(days=1)
            friday_count += int(second_friday_of_month.isoweekday() == 5)

        now = Helpers.pacific_now()
        one_year_ago = now + timedelta(days=-365)
        last_month_start = now
        last_month_end = None
        month_change = False
        while not month_change:
            current_month = last_month_start.month
            last_month_start = last_month_start + timedelta(days=-1)
            month_after_subtract = last_month_start.month

            month_change = not (current_month == month_after_subtract)
            if month_change:
                last_month_start_cpy = datetime(last_month_start.year, last_month_start.month, last_month_start.day)
                last_month_start = datetime(last_month_start.year, last_month_start.month, 1)
                last_month_end = datetime(last_month_start_cpy.year, last_month_start_cpy.month, last_month_start_cpy.day, 23, 59, 59)

        rep_ids_to_query = ["-1"]
        app_ids_to_query = ["-1"]
        pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.rep_submission_date >= one_year_ago)
        keepers = []
        for pp_sub in pp_subs:
            info = json.loads(pp_sub.extra_info)
            if "project_management_checkoffs" in info.keys():
                if "install" in info["project_management_checkoffs"].keys():
                    if "checked" in info["project_management_checkoffs"]["install"].keys():
                        if info["project_management_checkoffs"]["install"]["checked"]:
                            if "date" in info["project_management_checkoffs"]["install"].keys():
                                dt_vals = info["project_management_checkoffs"]["install"]["date"].split("-")
                                dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                         
                                if (dt >= last_month_start) and (dt <= last_month_end):
                                    keepers.append(pp_sub)
                                    rep_ids_to_query.append(pp_sub.rep_identifier)
                                    app_ids_to_query.append(pp_sub.field_application_identifier)

        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        app_identifier_name_dict = {}
        app_identifier_office_dict = {}
        office_ids_to_query = ["-1"]
        for app_entry in app_entries:
            app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
            app_identifier_office_dict[app_entry.identifier] = app_entry.office_identifier
            if not app_entry.office_identifier in office_ids_to_query:
                office_ids_to_query.append(app_entry.office_identifier)

        office_identifier_market_dict = {}
        office_identifier_solar_pro_managers_dict = {}
        offices = OfficeLocation.query(OfficeLocation.identifier.IN(office_ids_to_query))
        for office in offices:
            office_identifier_market_dict[office.identifier] = office.parent_identifier
            office_identifier_solar_pro_managers_dict[office.identifier] = []
            managers = FieldApplicationUser.query(
                ndb.AND(
                    FieldApplicationUser.main_office == office.identifier,
                    FieldApplicationUser.user_type == "solar_pro_manager",
                    FieldApplicationUser.current_status == 0
                )
            )
            for manager in managers:
                office_identifier_solar_pro_managers_dict[office.identifier].append({"identifier": manager.identifier, "name": manager.first_name.strip().title() + " " + manager.last_name.strip().title()})

        rep_identifier_name_dict = {}
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
        for rep in reps:
            rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

        pricing_structures = Helpers.get_pricing_structures()

        for keeper in keepers:
            app_identifier = keeper.field_application_identifier
            office_identifier = app_identifier_office_dict[app_identifier]
            if len(office_identifier_solar_pro_managers_dict[office_identifier]) > 0:
                market_identifier = office_identifier_market_dict[office_identifier]

                descrip = "SP Manager override for " + app_identifier_name_dict[app_identifier] + "'s install. "
                if market_identifier in pricing_structures.keys():
                    if "solar_pro_managers_override_amount" in pricing_structures[market_identifier].keys():
                        amount = pricing_structures[market_identifier]["solar_pro_managers_override_amount"]
                        amount = amount.replace("$", "")
                        amount = amount.replace(",", "")
                        amount = float(amount)

                        gross = amount / float(len(office_identifier_solar_pro_managers_dict[office_identifier]))
                        dollarss = int(gross)
                        centss = gross - dollarss
                        centss *= 100
                        centss = int(centss)

                        descrip += "An amount of " + Helpers.currency_format(amount) + " is divided into " + str(len(office_identifier_solar_pro_managers_dict[office_identifier])) + " equal part(s) amongst ("
                        names = []
                        for item in office_identifier_solar_pro_managers_dict[office_identifier]:
                            names.append(item["name"])
                        descrip += (", ".join(names))
                        descrip += ")."
                        descrip += " Amount is " + Helpers.currency_format(gross)
                        descrip += "."

                        if dollarss > 0 or centss > 0:
                            for item in office_identifier_solar_pro_managers_dict[office_identifier]:

                                transaction = MonetaryTransactionV2(
                                    approved=True,
                                    cents=centss,
                                    check_number=-1,
                                    created=h_p_n,
                                    denied=False,
                                    description=descrip,
                                    description_key="solar_pro_manager_override",
                                    dollars=dollarss,
                                    extra_info="{}",
                                    field_app_identifier=app_identifier,
                                    identifier=Helpers.guid(),
                                    paid=False,
                                    payout_date=second_friday_of_month,
                                    recipient=item["identifier"]
                                )
                                transactions.append(transaction)
                                docs_to_put.append(
                                    search.Document(
                                        fields=[
                                            search.TextField(name="identifier", value=transaction.identifier),
                                            search.TextField(name="description", value=transaction.description)
                                        ]
                                    )
                                )

        if len(transactions) == 1:
            transactions[0].put()
        elif len(transactions) > 1:
            ndb.put_multi(transactions)


    elif self.request.get("fn") == "rep_commissions":
        h_p_n = Helpers.pacific_now()

        second_friday_of_month = datetime(h_p_n.year, h_p_n.month, 1)
        friday_count = int(second_friday_of_month.isoweekday() == 5)
        while not friday_count == 2:
            second_friday_of_month = second_friday_of_month + timedelta(days=1)
            friday_count += int(second_friday_of_month.isoweekday() == 5)

        now = Helpers.pacific_now()
        one_year_ago = now + timedelta(days=-365)
        last_month_start = now
        last_month_end = None
        month_change = False
        while not month_change:
            current_month = last_month_start.month
            last_month_start = last_month_start + timedelta(days=-1)
            month_after_subtract = last_month_start.month

            month_change = not (current_month == month_after_subtract)
            if month_change:
                last_month_start_cpy = datetime(last_month_start.year, last_month_start.month, last_month_start.day)
                last_month_start = datetime(last_month_start.year, last_month_start.month, 1)
                last_month_end = datetime(last_month_start_cpy.year, last_month_start_cpy.month, last_month_start_cpy.day, 23, 59, 59)

        rep_ids_to_query = ["-1"]
        app_ids_to_query = ["-1"]
        pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.rep_submission_date >= one_year_ago)
        keepers = []
        for pp_sub in pp_subs:
            info = json.loads(pp_sub.extra_info)
            if "project_management_checkoffs" in info.keys():
                if "install" in info["project_management_checkoffs"].keys():
                    if "checked" in info["project_management_checkoffs"]["install"].keys():
                        if info["project_management_checkoffs"]["install"]["checked"]:
                            if "date" in info["project_management_checkoffs"]["install"].keys():
                                dt_vals = info["project_management_checkoffs"]["install"]["date"].split("-")
                                dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                         
                                if (dt >= last_month_start) and (dt <= last_month_end):
                                    keepers.append(pp_sub)
                                    rep_ids_to_query.append(pp_sub.rep_identifier)
                                    app_ids_to_query.append(pp_sub.field_application_identifier)

        app_identifier_lead_generator_dict = {}
        app_identifier_name_dict = {}
        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        for app_entry in app_entries:
            app_identifier_lead_generator_dict[app_entry.identifier] = app_entry.lead_generator
            app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
            if not app_entry.lead_generator == "-1":
                rep_ids_to_query.append(app_entry.lead_generator)

        rep_identifier_name_dict = {}
        rep_identifier_office_dict = {}
        rep_identifier_user_type_dict = {}
        office_ids_to_query = ["-1"]
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
        rep_identifier_compensation_dict = {}
        for rep in reps:
            rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
            rep_identifier_office_dict[rep.identifier] = rep.main_office
            rep_identifier_user_type_dict[rep.identifier] = rep.user_type
            office_ids_to_query.append(rep.main_office)
            rep_identifier_compensation_dict[rep.identifier] = {"self": float(0), "lead": float(0)}

        office_identifier_market_identifier_dict = {}
        offices = OfficeLocation.query(OfficeLocation.identifier.IN(office_ids_to_query))
        for office in offices:
            office_identifier_market_identifier_dict[office.identifier] = office.parent_identifier

        pricing_structures = Helpers.get_pricing_structures()
        for rep_identifier in rep_identifier_compensation_dict.keys():
            office_identifier = rep_identifier_office_dict[rep_identifier]
            market_key = office_identifier_market_identifier_dict[office_identifier]

            if market_key in pricing_structures.keys():
                user_type = rep_identifier_user_type_dict[rep_identifier]
                self_key = ["energy_expert_self_gen_commission_per_kw", "sales_manager_self_gen_commission_per_kw"][int(user_type == "sales_manager")]
                lead_key = ["energy_expert_commission_per_kw", "sales_manager_commission_per_kw"][int(user_type == "sales_manager")]

                if self_key in pricing_structures[market_key].keys():
                    value = str(pricing_structures[market_key][self_key]).replace("$", "").replace(",", "")
                    rep_identifier_compensation_dict[rep_identifier]["self"] = float(value)

                if lead_key in pricing_structures[market_key].keys():
                    value = str(pricing_structures[market_key][lead_key]).replace("$", "").replace(",", "")
                    rep_identifier_compensation_dict[rep_identifier]["lead"] = float(value)


        kv_keys_to_query1 = ["-1"]
        kv_keys_to_query2 = ["-1"]
        for rep_identifier in rep_identifier_compensation_dict.keys():
            kv_keys_to_query1.append("commission_per_self_gen_sale_" + rep_identifier)
            kv_keys_to_query2.append("commission_per_lead_sale_" + rep_identifier)

        kv_ones = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(kv_keys_to_query1))
        for kv in kv_ones:
            rep_identifier = kv.keyy.replace("commission_per_self_gen_sale_", "")
            rep_identifier_compensation_dict[rep_identifier]["self"] = float(kv.val.replace("$", "").replace(",", ""))
        
        kv_twos = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(kv_keys_to_query2))
        for kv in kv_twos:
            rep_identifier = kv.keyy.replace("commission_per_lead_sale_", "")
            rep_identifier_compensation_dict[rep_identifier]["lead"] = float(kv.val.replace("$", "").replace(",", ""))

        app_identifier_system_size_dict = {}
        proposals = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(app_ids_to_query))
        for proposal in proposals:
            proposal.fix_additional_amount()
            proposal.fix_system_size()

            app_identifier_system_size_dict[proposal.field_app_identifier] = float(json.loads(proposal.info)["system_size"])

        transactions = []
        for keeper in keepers:
            app_id = keeper.field_application_identifier
            rep_identifier = keeper.rep_identifier
            is_lead = (len(app_identifier_lead_generator_dict[app_id]) == 128)
            dollarss = 0
            centss = 0
            descrip = ""
            system_size = app_identifier_system_size_dict[app_id]
            compensation_dict = rep_identifier_compensation_dict[rep_identifier]
            if is_lead:
                solar_pro = rep_identifier_name_dict[app_identifier_lead_generator_dict[app_id]]
                gross = system_size * compensation_dict["lead"]
                dollarss = int(gross)
                centss = gross - dollarss
                centss *= 100
                centss = int(centss)

                descrip = "Sold a " + str(system_size) + " KW system to " + app_identifier_name_dict[app_id] + " via " + solar_pro + "'s AB. " + Helpers.currency_format(compensation_dict["lead"]) + " per KW is awarded. "
                descrip += Helpers.currency_format(compensation_dict["lead"]) + " * " + str(system_size) + " = " + Helpers.currency_format(gross)
                descrip += "."
            else:                
                gross = system_size * compensation_dict["self"]
                dollarss = int(gross)
                centss = gross - dollarss
                centss *= 100
                centss = int(centss)

                descrip = "Sold a " + str(system_size) + " KW system to " + app_identifier_name_dict[app_id] + ". " + Helpers.currency_format(compensation_dict["self"]) + " per KW is awarded. "
                descrip += Helpers.currency_format(compensation_dict["self"]) + " * " + str(system_size) + " = " + Helpers.currency_format(gross)
                descrip += "."

            transaction = MonetaryTransactionV2(
                approved=True,
                cents=centss,
                check_number=-1,
                created=h_p_n,
                denied=False,
                description=descrip,
                description_key="rep_sales_commission_C",
                dollars=dollarss,
                extra_info="{}",
                field_app_identifier=app_id,
                identifier=Helpers.guid(),
                paid=False,
                payout_date=second_friday_of_month,
                recipient=rep_identifier
            )
            if dollarss > 0 or centss > 0:
                transactions.append(transaction)

                docs_to_put.append(
                    search.Document(
                        fields=[
                            search.TextField(name="identifier", value=transaction.identifier),
                            search.TextField(name="description", value=transaction.description)
                        ]
                    )
                )

        if len(transactions) > 1:
            ndb.put_multi(transactions)
        elif len(transactions) == 1:
            transactions[0].put()

    if len(docs_to_put) > 0:
        s_index.put(docs_to_put)



