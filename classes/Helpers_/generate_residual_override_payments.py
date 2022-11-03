@staticmethod
def generate_residual_override_payments(amount, months, recip, originator, app_entry):
    from google.appengine.api import search
    docs_to_put = []
    today = Helpers.pacific_today()
    quarter_start_date = Helpers.jump_to_next_quarter(today)
    quarter_start_date = datetime(quarter_start_date.year, quarter_start_date.month, quarter_start_date.day)
    payment_dates = []
    friday_count = int(quarter_start_date.isoweekday() == 5)
    while friday_count < 2:
        quarter_start_date = quarter_start_date + timedelta(days=1)
        friday_count += int(quarter_start_date.isoweekday() == 5)
    payment_dates.append(quarter_start_date.date())

    while len(payment_dates) < months:
        month_changed = False
        curr_month = quarter_start_date.month
        while not month_changed:
            quarter_start_date = quarter_start_date + timedelta(days=1)
            month_changed = not (quarter_start_date.month == curr_month)

        friday_count = int(quarter_start_date.isoweekday() == 5)
        while friday_count < 2:
            quarter_start_date = quarter_start_date + timedelta(days=1)
            friday_count += int(quarter_start_date.isoweekday() == 5)
        payment_dates.append(quarter_start_date.date())

    dollar_amount = round((amount / float(months)), 2)
    dollars = int(dollar_amount)
    cents = ((round(dollar_amount - float(int(dollar_amount)), 2)) * 100)
    cents = round(cents, 2)
    cents = int(cents)

    if dollars + cents > 0:
        cnt = 1
        for payment_date in payment_dates:
            descrip = "Override Payment on " + originator.first_name.strip().title() + " " + originator.last_name.strip().title() + " selling a system to " + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + "."
            v2_transaction = MonetaryTransactionV2(
                approved=True,
                cents=cents,
                check_number=-1,
                created=Helpers.pacific_now(),
                denied=False,
                description=descrip,
                description_key="residual_override_" + str(payment_date.year) + "_" + str(payment_date.month),
                dollars=dollars,
                extra_info="{}",
                field_app_identifier=app_entry.identifier,
                identifier=Helpers.guid(),
                paid=False,
                payout_date=payment_date,
                recipient=recip
            )
            v2_transaction.put()
            docs_to_put.append(
                search.Document(
                    fields=[
                        search.TextField(name="identifier", value=v2_transaction.identifier),
                        search.TextField(name="description", value=v2_transaction.description)
                    ]
                )
            )
            cnt += 1
            
        transaction_index = search.Index(name="v2_transactions")
        transaction_index.put(docs_to_put)

