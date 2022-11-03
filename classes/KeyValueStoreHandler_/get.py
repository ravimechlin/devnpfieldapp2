def get(self, keyyy):
    self.response.content_type = "application/json"
    ret_json = {}
    ret_json["success"] = False
    ret_json["key"] = keyyy
    ret_json["value"] = None
    # if there's a comma assume multiple mode

    mode = "single"
    pipe_count = 0
    chars = list(keyyy)

    for char in chars:
        if char == "|":
            pipe_count += 1

            if pipe_count == 3:
                mode = "multiple"
        else:
            pipe_count = 0

    if mode == "single":
        result = KeyValueStoreItem.first(
            ndb.OR
            (
                ndb.AND
                (
                    KeyValueStoreItem.keyy == keyyy,
                    KeyValueStoreItem.expiration > Helpers.pacific_now(),
                ),
                ndb.AND
                (
                    KeyValueStoreItem.keyy == keyyy,
                    KeyValueStoreItem.expiration == datetime(1970, 1, 1)
                )
            )
        )


        if not result is None:
            ret_json["expiration"] = result.expiration.strftime("%Y-%m-%d %H:%M:%S")
            ret_json["success"] = True
            ret_json["value"] = result.val
    else:
        keyyys = keyyy.split("|||")
        del ret_json["key"]
        ret_json["keys"] = keyyys
        query = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(keyyys))
        ret_json["values"] = []
        ret_json["expirations"] = []

        count = 0
        while count < len(keyyys):
            ret_json["values"].append(None)
            ret_json["expirations"].append(None)
            count += 1

        for item in query:
            ret_json["success"] = True
            idx = keyyys.index(item.keyy)
            # Does this lose the keys and just returns an array of values?
            ret_json["expirations"][idx] = item.expiration.strftime("%Y-%m-%d %H:%M:%S")
            ret_json["values"][idx] = item.val


    self.response.out.write(json.dumps(ret_json))

