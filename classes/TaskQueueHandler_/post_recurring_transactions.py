def post_recurring_transactions(self):
    import json
    f = GCSLockedFile("/ApplicationSettings/recurring_transactions.json")
    transactions = json.loads(f.read())
    f.unlock()

    p_date = Helpers.pacific_now()    

    if self.request.get("frequency") == "monthly":
        next_month = p_date.month + 1
        year = p_date.year
        if next_month == 13:
            next_month = 1
            year += 1
        p_date = datetime(year, next_month, 1, 12, 0, 0)

    while not p_date.isoweekday() == 5:
        p_date = p_date + timedelta(days=1)

    p_date = p_date.date()

    keepers = []
    for t in transactions:
        if t["frequency"] == self.request.get("frequency") and t["active"]:
            keepers.append(t)

    debts_to_put = []
    transactions_to_put = []
    docs_to_put = []

    for keeper in keepers:
        aaa = keeper["payload"]["amount"]
        ddd = keeper["payload"]["description"]
        ttt = keeper["payload"]["trans_type"]

        payout = p_date
        amt = float(aaa)
        centss = int((float(amt) - float(int(amt))) * float(100))

        s_index = search.Index(name="v2_transactions")

        for r in keeper["recipients"]:
            debt_to_put = None
            doc_to_put = None
            trans_to_put = None
            if ttt == "collection":
                amt *= -1
                centss *= -1
                debt = UserDebt.first(UserDebt.field_app_identifier == r)
                if not debt is None:
                    debt_items = json.loads(debt.items)
                    debt_items.append({"date": str(payout), "amount": float(aaa) * float(-1), "description": ddd})
                    debt.items = json.dumps(debt_items)
                    debt.total += debt_items[len(debt_items) - 1]["amount"]
                    debt_to_put = debt

            if ttt == "advance":
                debt = UserDebt.first(UserDebt.field_app_identifier == r)
                if not debt is None:
                    debt_items = json.loads(debt.items)
                    debt_items.append({"date": str(payout), "amount": float(aaa), "description": ddd})
                    debt.items = json.dumps(debt_items)
                    debt.total += debt_items[len(debt_items) - 1]["amount"]
                    debt_to_put = debt

            amt_rounded = float(amt)
            amt_rounded = round(amt_rounded, 2)
            dollars2 = int(amt)
            cents2 = (amt - float(dollars2))
            cents2 *= float(100)
            cents2 = round(cents2, 0)
            cents2 = int(cents2)


            v2trans = MonetaryTransactionV2(
                identifier=Helpers.guid(),
                description=ddd,
                dollars=dollars2,
                cents=cents2,
                approved=True,
                denied=False,
                description_key="n/a",
                recipient=r,
                created=Helpers.pacific_now(),
                check_number=-1,
                payout_date=p_date,
                paid=False,
                field_app_identifier="n/a",
                extra_info="{}"
            )
            if ttt == "reimbursement":
                v2trans.description_key = keeper["payload"]["reimbursement_type"]
                v2trans.extra_info = json.dumps({"file_extension": "jpg"})

            cp = CheckPayment.first(
                ndb.AND
                (
                    CheckPayment.recipient == v2trans.recipient,
                    CheckPayment.check_date == v2trans.payout_date
                )
            )

            if cp is None:
                trans_to_put = v2trans
                doc_to_put = search.Document(
                    fields=[
                        search.TextField(name="identifier", value=v2trans.identifier),
                        search.TextField(name="description", value=v2trans.description)
                    ]
                )
                Helpers.gcs_copy("/Images/Receipts/missing_receipt.jpg", "Images/Receipts/" + v2trans.identifier + ".jpg", "image/jpg", "public-read")
                
            if (not (debt_to_put is None)):
                debts_to_put.append(debt_to_put)

            if not ttt == "advance":
                if (not (trans_to_put is None)):
                    transactions_to_put.append(trans_to_put)
                if (not (doc_to_put is None)):
                    docs_to_put.append(doc_to_put)
            else:
                put_transaction = True
                if "do_not_generate_payout" in keeper.keys():
                    if keeper["do_not_generate_payout"] == "1":
                        put_transaction = False
                if put_transaction:
                    if (not (trans_to_put is None)):
                        transactions_to_put.append(trans_to_put)
                    if (not (doc_to_put is None)):
                        docs_to_put.append(doc_to_put)

    if len(debts_to_put) > 0:
        x = 5
        ndb.put_multi(debts_to_put)
    if len(transactions_to_put) > 0:
        ndb.put_multi(transactions_to_put)
    if len(docs_to_put) > 0:
        s_index.put(docs_to_put)
