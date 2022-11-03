def miles_driven(self):
    from google.appengine.api import search
    h_p_t = Helpers.pacific_today()

    
    start_dt = datetime(h_p_t.year, h_p_t.month, 1)
    start_dt = start_dt + timedelta(days=-1)
    while not start_dt.day == 1:
        start_dt = start_dt + timedelta(days=-1)


    end_dt = datetime(start_dt.year, start_dt.month, start_dt.day, 23, 59, 59)
    curr_month = end_dt.month
    while end_dt.month == curr_month:
        end_dt = end_dt + timedelta(days=1)
    end_dt = end_dt + timedelta(days=-1)



    surveys = WeeklySurvey.query(
        ndb.AND(
            WeeklySurvey.submitted >= start_dt,
            WeeklySurvey.submitted <= end_dt
        )
    )

    rep_identifier_miles_driven_dict = {}
    rep_identifier_miles_driven_details_dict = {}
    rep_identifier_dt_dict = {}
    for survey in surveys:
        if survey.user_type in ["energy_expert", "sales_manager"]:
            data = json.loads(survey.response)
            if "miles_driven" in data.keys():
                if not survey.rep_identifier in rep_identifier_dt_dict.keys():
                    rep_identifier_dt_dict[survey.rep_identifier] = []
                dt = survey.week_dt
                if not dt in rep_identifier_dt_dict[survey.rep_identifier]:                
                    rep_identifier_dt_dict[survey.rep_identifier].append(dt)
                    try:
                        parsed = float(data["miles_driven"])
                        parsed = round(parsed, 2)
                    except:
                        Helpers.send_email("rnirnber@gmail.com", "bad miles", survey.identifier)

                    if not survey.rep_identifier in rep_identifier_miles_driven_dict.keys():
                        rep_identifier_miles_driven_dict[survey.rep_identifier] = float(0)
                    rep_identifier_miles_driven_dict[survey.rep_identifier] += parsed

                    if not survey.rep_identifier in rep_identifier_miles_driven_details_dict.keys():
                        rep_identifier_miles_driven_details_dict[survey.rep_identifier] = []
                    obj = {"dt": str(survey.submitted.date()), "miles": str(parsed)}
                    rep_identifier_miles_driven_details_dict[survey.rep_identifier].append(obj)
                    rep_identifier_dt_dict[survey.rep_identifier].append(dt)

    docs_to_put = []
    transactions_to_put = []

    h_p_n = Helpers.pacific_now()
    payment_date = datetime(h_p_n.year, h_p_n.month, 1)
    friday_count = int(payment_date.isoweekday() == 5)
    while friday_count < 2:
        payment_date = payment_date + timedelta(days=1)
        friday_count += int(payment_date.isoweekday() == 5)

    transaction_index = search.Index(name="v2_transactions")

    for rep_identifier in rep_identifier_miles_driven_details_dict.keys():
        total_miles = rep_identifier_miles_driven_dict[rep_identifier]
        per_mile = 0.56
        dollar_amount = total_miles * per_mile
        dollar_amount = round(dollar_amount, 2)
        
        descrip = "Mileage reimbursement for weekly reports submitted between " + str(start_dt.date()) + " - " + str(end_dt.date()) + ". "
        for item in rep_identifier_miles_driven_details_dict[rep_identifier]:
            descrip += str(item["miles"]) + " miles were reported on " + str(item["dt"]) + ". "
        descrip += str(total_miles) + " * 0.56 = " + Helpers.currency_format(dollar_amount)
        descrip += "."

        dollars = int(dollar_amount)
        cents = float(dollar_amount) - float(dollars)
        cents *= float(100)
        cents = int(cents)

        extra_info_dct = {}
        extra_info_dct["file_extension"] = "jpg"
        e_info = json.dumps(extra_info_dct)

        if dollars > 0 or cents > 0:
            v2_transaction = MonetaryTransactionV2(
                approved=True,
                cents=cents,
                check_number=-1,
                created=h_p_n,
                denied=False,
                description=descrip,
                description_key="reimbursement_other",
                dollars=dollars,
                extra_info=e_info,
                field_app_identifier="n/a",
                identifier=Helpers.guid(),
                paid=False,
                payout_date=payment_date,
                recipient=rep_identifier
            )

            Helpers.gcs_copy("/Images/Receipts/missing_receipt.jpg", "Images/Receipts/" + v2_transaction.identifier + ".jpg", "image/jpg", "public-read")

            transactions_to_put.append(v2_transaction)
            docs_to_put.append(
                search.Document(
                    fields=[
                        search.TextField(name="identifier", value=v2_transaction.identifier),
                        search.TextField(name="description", value=v2_transaction.description)
                    ]
                )
            )
    
    
    transaction_index.put(docs_to_put)
    ndb.put_multi(transactions_to_put)

