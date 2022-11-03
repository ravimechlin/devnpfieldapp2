def transaction_history_for_quadrant(self):
    self.response.content_type = "application/json"
    ret_json = {"items": []}
    transaction_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "transaction_log_" + self.request.get("identifier"))
    if not transaction_kv is None:
        ret_json["items"] = json.loads(transaction_kv.val)

    self.response.out.write(json.dumps(ret_json))

