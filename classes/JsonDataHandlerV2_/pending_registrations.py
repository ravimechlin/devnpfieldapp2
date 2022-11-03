def pending_registrations(self):
    ret_json = {"data": []}
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pending_registrations")
    if not kv is None:
        user_identifiers = json.loads(kv.val)

        app_users = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(user_identifiers))
        for user in app_users:
            ret_json["data"].append({"identifier": user.identifier, "name": user.first_name.strip().title() + " " + user.last_name.strip().title()})
    self.response.content_type = "application/json"
    self.response.out.write(json.dumps(ret_json))
