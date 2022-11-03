def payroll_disqualification(self):
    from google.appengine.api import taskqueue
    if str(self.request.get("identifiers")) == "[]":
        return
    elif str(self.request.get("identifiers")).lower() in ["", "none"]:
        rep_identifiers = []
        pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.rep_submission_date >= (Helpers.pacific_now() + timedelta(days=-365)))
        for pp_sub in pp_subs:
            if not pp_sub.rep_identifier in rep_identifiers:
                rep_identifiers.append(pp_sub.rep_identifier)

        taskqueue.add(url="/tq/payroll_disqualification", params={"identifiers": json.dumps(rep_identifiers)})
    else:
        identifiers = json.loads(self.request.get("identifiers"))
        identifier = identifiers[0]
        new_identifiers = []
        if len(identifiers) > 1:
            new_identifiers = identifiers[1:]
        
        start_dt = Helpers.pacific_now()
        month_change = False
        start_month = start_dt.month
        while not month_change:
            start_dt = start_dt + timedelta(days=-1)
            month_change = ( not (start_dt.month == start_month) )
        start = date(start_dt.year, start_dt.month, 1)

        end_dt = Helpers.pacific_now()
        month_change = False
        end_month = end_dt.month
        while not month_change:
            end_dt = end_dt + timedelta(days=-1)
            month_change = ( not (end_dt.month == end_month) )
        end = end_dt.date()

        pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.rep_identifier == identifier)
        lead_kvs_to_query = ["-1"]
        wc_complete_tally = 0
        for pp_sub in pp_subs:
            info = json.loads(pp_sub.extra_info)
            if "project_management_checkoffs" in info.keys():
                if "welcome_call_completed" in info["project_management_checkoffs"].keys():
                    if isinstance(info["project_management_checkoffs"]["welcome_call_completed"], dict):
                        if "checked" in info["project_management_checkoffs"]["welcome_call_completed"].keys():
                            if info["project_management_checkoffs"]["welcome_call_completed"]["checked"]:
                                if "date" in info["project_management_checkoffs"]["welcome_call_completed"].keys():
                                    dt_vals = info["project_management_checkoffs"]["welcome_call_completed"]["date"].split("-")
                                    dt = date(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                                    wc_complete_tally += int( (dt >= start and dt <= end) )

                                    if dt >= start and dt <= end:
                                        lead_kvs_to_query.append("lead_status_" + pp_sub.field_application_identifier)

        lead_kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(lead_kvs_to_query))
        for lead_kv in lead_kvs:
            if lead_kv.val == "1":
                wc_complete_tally -= 1

        minimum_deals = 99
        pricing_structures = Helpers.get_pricing_structures()
        rep = FieldApplicationUser.first(FieldApplicationUser.identifier == identifier)
        if not rep is None:   
            ol = OfficeLocation.first(OfficeLocation.identifier == rep.main_office)
            if not ol is None:
                market_key = ol.parent_identifier
                if market_key in pricing_structures.keys():
                    if "residual_eligibility_monthly_deal_minimum" in pricing_structures[market_key].keys():
                        minimum_deals = int(pricing_structures[market_key]["residual_eligibility_monthly_deal_minimum"])

        transaction_start = datetime(end.year, end.month, end.day) + timedelta(days=1)
        transaction_start = transaction_start.date()
        transaction_end = datetime(transaction_start.year, transaction_start.month, transaction_start.day)
        end_month = transaction_end.month
        month_change = False
        while not month_change:
            transaction_end = transaction_end + timedelta(days=1)
            month_change = ( not (transaction_end.month == end_month) )
        transaction_end = transaction_end + timedelta(days=-1)
        transaction_end = transaction_end.date()
        
        
        rep_eligible = (wc_complete_tally >= minimum_deals)
        if not rep_eligible:
            transactions = MonetaryTransactionV2.query(
                ndb.AND(
                    MonetaryTransactionV2.recipient == identifier,
                    MonetaryTransactionV2.payout_date >= transaction_start,
                    MonetaryTransactionV2.payout_date <= transaction_end
                )
            )
            for t in transactions:
                if "residual_override_" in t.description_key or "residual_pay_" in t.description_key:
                    t.key.delete()
        #f = GCSLockedFile("/Temp/june_wc_complete")
        #content = f.read()
        #if content is None:
            #content = "{}"
        #content = json.loads(content)
        #content[identifier] = {"tally": wc_complete_tally, "meets_criteria": wc_complete_tally >= minimum_deals}
        #f.write(json.dumps(content), "text/plain", "public-read")  

        taskqueue.add(url="/tq/payroll_disqualification", params={"identifiers": json.dumps(new_identifiers)})

