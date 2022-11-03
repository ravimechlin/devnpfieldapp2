def get_phone_call_for_lead(self):
    self.response.content_type = "application/json"
    ret_json = {"phone_call": None}
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "ab_call_recording_" + self.request.get("identifier"))
    if not kv is None:
        ret_json["phone_call"] = kv.val
    self.response.out.write(json.dumps(ret_json))

