@staticmethod
def generate_residual_payments_for_deal(recip, app_entry, market_key, proposal, months, description_key_prefix):
    from google.appengine.api import search
    transaction_index = search.Index(name="v2_transactions")
    docs_to_put = []
    today = Helpers.pacific_today()
    pricing_structures = Helpers.get_pricing_structures()
    amount_per_kw = float(0)
    if market_key in pricing_structures.keys():
        if "residual_pay_per_kw" in pricing_structures[market_key].keys():
            amount_per_kw = float(pricing_structures[market_key]["residual_pay_per_kw"].replace("$", "").replace(",", ""))
    if amount_per_kw > float(0):
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

        proposal.fix_additional_amount()
        proposal.fix_system_size()
        prop_info = json.loads(proposal.info)
        per_kw_amount = round(amount_per_kw, 2)
        dollar_amount = round((amount_per_kw * float(prop_info["system_size"])) / float(months), 2)
        deal_points = Helpers.get_points_for_deal(proposal)
        cost_per_points = 0
        original_dollar_amount = dollar_amount
        if deal_points > float(0):
            cost_per_points = round(float(str(Helpers.read_setting("services_point_cost")).replace("$", "").replace(",", "")), 2)
            dollar_amount = (amount_per_kw * float(prop_info["system_size"])) - (0.5 * cost_per_points * deal_points * float(prop_info["system_size"]))
            dollar_amount /= float(months)
            dollar_amount = round(dollar_amount, 2)

        dollars = int(dollar_amount)
        cents = ((round(dollar_amount - float(int(dollar_amount)), 2)) * 100)
        cents = round(cents, 2)
        cents = int(cents)

        if dollars + cents > 0:
            cnt = 1
            for payment_date in payment_dates:
                descrip = "Residual Payment Month #" + str(cnt) + " for " + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + "... "
                descrip += "System Size was " + str(round(float(prop_info["system_size"]), 2)) + "... "
                descrip += "($" + str(round(float(prop_info["system_size"]), 2)) + " * $" + str(per_kw_amount) + " per KW)  / " + str(months) + " = $" + str(round(original_dollar_amount, 2)) + "... "
                d_a = round(float(prop_info["system_size"]) * amount_per_kw, 2)
                if(deal_points > float(0)):
                    descrip += "There was also a point cost for this deal. "
                    descrip += str(round(deal_points, 2))
                    descrip += " points at $"
                    descrip += str(round(cost_per_points, 2))
                    descrip += ". "
                    descrip += Helpers.currency_format(d_a)
                    descrip += " - ("
                    descrip += Helpers.currency_format(deal_points)
                    descrip += " * "
                    descrip += Helpers.currency_format(cost_per_points)
                    descrip += " * "
                    descrip += str(round(float(prop_info["system_size"]), 2))
                    descrip += " * 0.5 ) / "
                    descrip += str(months)
                    descrip += " = "
                    descrip += Helpers.currency_format(dollar_amount)
                    descrip += "."

                v2_transaction = MonetaryTransactionV2(
                    approved=True,
                    cents=cents,
                    check_number=-1,
                    created=Helpers.pacific_now(),
                    denied=False,
                    description=descrip,
                    description_key=description_key_prefix + "_" + str(payment_date.year) + "_" + str(payment_date.month),
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
            transaction_index.put(docs_to_put)

