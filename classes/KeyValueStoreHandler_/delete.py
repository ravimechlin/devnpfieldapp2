def delete(self, keyyy="*"):
    if keyyy is None:
        key = "*"
    self.response.content_type = "application/json"
    deleted = 0
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
        if keyyy == "*":
            #now = Helpers.pacific_now()
            #existing_items = KeyValueStoreItem.query(
            #    ndb.AND
            #    (
            #        KeyValueStoreItem.expiration > datetime(1970, 1, 1),
            #        KeyValueStoreItem.expiration < now
            #    )
            #)
            #keys_to_delete = []
            #last_item = None
            #for existing_item in existing_items:
            #    last_item = existing_item
            #    keys_to_delete.append(existing_item.key)
            #    deleted+=1

            #if len(keys_to_delete) > 1:
            #    ndb.delete_multi(keys_to_delete)
            #elif len(keys_to_delete) == 1:
            #    if not last_item is None:
            #        last_item.key.delete()
            from google.appengine.api import taskqueue
            taskqueue.add(url="/tq/drop_expired_kvs", params={})
        
        else:
            existing_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == keyyy)
            if not existing_item is None:
                existing_item.key.delete()
                deleted+=1
    else:
        keyyys = keyyy.split("|||")
        existing_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(keyyys))
        for existing_item in existing_items:
            existing_item.key.delete()
            deleted+=1
        
    ret_json = {}
    ret_json['deleted'] = deleted
    self.response.out.write(json.dumps(ret_json))
