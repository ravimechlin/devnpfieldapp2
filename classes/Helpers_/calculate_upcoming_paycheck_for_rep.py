@staticmethod
def calculate_upcoming_paycheck_for_rep(rep_identifier, custom_date=False, dt=None):
    this_paycheck_date = Helpers.pacific_now()
    if custom_date:
        this_paycheck_date = dt
    if this_paycheck_date.isoweekday() == 6:
        this_paycheck_date = this_paycheck_date + timedelta(days=-1)
    else:
        while not (this_paycheck_date.isoweekday() == 5):
            this_paycheck_date = this_paycheck_date + timedelta(days=1)

    this_paycheck_date = this_paycheck_date.date()            
    ret_dict = {}
    ret_dict["transactions"] = []
    transactions = MonetaryTransactionV2.query(
        ndb.AND
        (
            MonetaryTransactionV2.payout_date == this_paycheck_date,
            MonetaryTransactionV2.recipient == rep_identifier,
            MonetaryTransactionV2.approved == True,
            MonetaryTransactionV2.denied == False
        )
    )

    monetary_transactions_cpy = []
    for transaction in transactions:        
        monetary_transactions_cpy.append(transaction)

    monetary_transactions_cpy = Helpers.bubble_sort(monetary_transactions_cpy, "created")

    total = 0
    for transaction in monetary_transactions_cpy:
        transaction_item = {}
        transaction_item["identifier"] = transaction.identifier
        transaction_item["amount"] = (transaction.dollars * 100) + transaction.cents
        transaction_item["description"] = transaction.description
        transaction_item["description_key"] = transaction.description_key
        transaction_item["recorded"] = str(transaction.created)
        transaction_item["effective"] = str(transaction.created)
        transaction_item["check_number"] = transaction.check_number
        total += transaction_item["amount"]

        ret_dict["transactions"].append(transaction_item)

    now = Helpers.pacific_now()
    paycheck_dt = datetime(this_paycheck_date.year, this_paycheck_date.month, this_paycheck_date.day, now.hour, now.minute, now.second)

    diff = (now - paycheck_dt).total_seconds()

    ret_dict["ready"] = (not (KeyValueStoreItem.first(KeyValueStoreItem.keyy == "paycheck_preview_ready_" + str(this_paycheck_date)) is None)) or (diff > (60 * 60 * 24 * 7))

    return ret_dict
