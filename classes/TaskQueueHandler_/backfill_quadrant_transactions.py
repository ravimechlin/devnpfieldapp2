def backfill_quadrant_transactions(self):
    return
    h_p_n = Helpers.pacific_now()
    quadrants = RepQuadrant.query()
    for quadrant in quadrants:
        transaction_info = []
        obj = {"msg": "The transaction log was created", "dt": str(h_p_n).split(".")[0]}
        transaction_info.append(obj)
        transaction_kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="transaction_log_" + quadrant.identifier,
            val=json.dumps(transaction_info),
            expiration=datetime(1970, 1, 1)
        )
        transaction_kv.put()
