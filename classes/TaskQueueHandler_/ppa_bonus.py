def ppa_bonus(self):
    pacific_now = Helpers.pacific_now()
    pacific_today = Helpers.pacific_today()

    def is_last_quarter(dt):
        target_year = None
        target_months = []
        month = pacific_now.month
        
        if month >= 1 and month <= 3:
            target_year = pacific_now.year - 1
            target_months = [10, 11, 12]
        elif month >= 4 and month <= 6:
            target_year = pacific_now.year
            target_months = [1, 2, 3]
        elif month >= 7 and month <= 9:
            target_year = pacific_now.year
            target_months = [4, 5, 6]
        else:
            target_year = pacific_now.year
            target_months = [7, 8, 9]

        return dt.year == target_year and dt.month in target_months
    
    one_year_ago = pacific_now + timedelta(days=-365)
    rep_identifier_install_tally_dict = {}

    pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.rep_submission_date >= one_year_ago)    
    rep_ids_to_query = ["-1"]
    booking_ids_to_query = ["-1"]
    for pp_sub in pp_subs:
        info = json.loads(pp_sub.extra_info)
        if "project_management_checkoffs" in info.keys():
            if "install" in info["project_management_checkoffs"].keys():
                data = info["project_management_checkoffs"]["install"]
                if "date" in data.keys():
                    dt_vals = data["date"].split("-")
                    dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                    if is_last_quarter(dt):
                        if not pp_sub.rep_identifier in rep_identifier_install_tally_dict.keys():
                            rep_identifier_install_tally_dict[pp_sub.rep_identifier] = 0

                        rep_identifier_install_tally_dict[pp_sub.rep_identifier] += 1
                        booking_ids_to_query.append(pp_sub.booking_identifier)
                        rep_ids_to_query.append(pp_sub.rep_identifier)

    reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
    rep_identifier_rep_id_dict = {}
    rep_id_rep_identifier_dict = {}
    for rep in reps:
        rep_identifier_rep_id_dict[rep.identifier] = rep.rep_id
        rep_id_rep_identifier_dict[rep.rep_id] = rep.identifier

    rep_identifier_ppa_tally_dict = {}
    bookings = SurveyBooking.query(SurveyBooking.identifier.IN(booking_ids_to_query))
    for booking in bookings:
        fund_name_components = booking.fund.split("_")
        if "ppa" in fund_name_components or "lease" in fund_name_components:
            if not rep_id_rep_identifier_dict[booking.associated_rep_id] in rep_identifier_ppa_tally_dict.keys():
                rep_identifier_ppa_tally_dict[rep_id_rep_identifier_dict[booking.associated_rep_id]] = 0

            rep_identifier_ppa_tally_dict[rep_id_rep_identifier_dict[booking.associated_rep_id]] += 1


    bonus_year = pacific_now.year
    bonus_months = []
    transaction_description = "PPA/Install Bonus for "    
    quarter_start = None
    if pacific_now.month in [1, 2, 3]:
        bonus_year = pacific_now.year - 1
        
    if pacific_now.month >= 1 and pacific_now.month <= 3:
        transaction_description += "October, November, and December"
        bonus_months = [10, 11, 12]
        quarter_start = datetime(pacific_now.year, 1, 1)
    elif pacific_now.month >= 4 and pacific_now.month <= 6:
        transaction_description += "January, February, and March"
        bonus_months = [1, 2, 3]
        quarter_start = datetime(pacific_now.year, 4, 1)
    elif pacific_now.month >= 7 and pacific_now.month <= 9:
        transaction_description += "April, May, and June"
        bonus_months = [4, 5, 6]
        quarter_start = datetime(pacific_now.year, 7, 1)
    else:
        transaction_description += "July, August, and September"
        bonus_months = [7, 8, 9]
        quarter_start = datetime(pacific_now.year, 10, 1)

    transaction_description += (" of " + str(bonus_year) + ".")
    transaction_description_key = "ppa_install_bonus_" + str(bonus_year) + "_" + "_".join(map(lambda m: str(m), bonus_months))

    ########################
    bonus_threshold_map = [
        {"floor": 7, "ceiling": 13, "amount": float(335)},
        {"floor": 14, "ceiling": 20, "amount": float(515)},
        {"floor": 21, "ceiling": 27, "amount": float(725)},
        {"floor": 28, "ceiling": 34, "amount": float(975)},
        {"floor": 35, "ceiling": 10000, "amount": float(1275)}
    ]

    fri_count = 0
    while fri_count < 2:
        fri_count += quarter_start.isoweekday() == 5
        quarter_start = quarter_start + timedelta(days=1)
    
    for rep_identifier in rep_identifier_ppa_tally_dict.keys():
        amount = float(0)
        ppa_tally = float(rep_identifier_ppa_tally_dict[rep_identifier])
        install_total = rep_identifier_install_tally_dict[rep_identifier]
        for threshold in bonus_threshold_map:
            if install_total >= threshold["floor"] and install_total <= threshold["ceiling"]:
                amount = threshold["amount"]

        transaction_amt = amount * ppa_tally
        if transaction_amt >= float(0.01):
            transaction_amt *= 100
            transaction_dollars = int(transaction_amt / float(100))
            transaction_cents = int(transaction_amt % float(100))            

            transaction_date = quarter_start.date()
            v2_transaction = MonetaryTransactionV2.first(
                ndb.AND(
                    MonetaryTransactionV2.recipient == rep_identifier,
                    MonetaryTransactionV2.description_key == transaction_description_key
                )
            )
            
            save = False
            if v2_transaction is None:
                save = True
                v2_transaction = MonetaryTransactionV2(
                    identifier=Helpers.guid(),
                    approved=True,
                    cents=transaction_cents,
                    check_number=-1,
                    created=Helpers.pacific_now(),
                    denied=False,
                    description=transaction_description,
                    description_key=transaction_description_key,
                    dollars=transaction_dollars,
                    extra_info="{}",
                    field_app_identifier="n/a",
                    paid=False,
                    payout_date=transaction_date,
                    recipient=rep_identifier
                )
            else:
                v2_transaction.dollars = transaction_dollars
                v2_transaction.cents = transaction_cents
                if pacific_today > v2_transaction.payout_date:
                    save = False
                else:
                    save = True

            if save:
                v2_transaction.put()


