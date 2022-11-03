def drop_expired_kvs(self):
    deleted = 0

    now = Helpers.pacific_now()
    existing_items = KeyValueStoreItem.query(
        ndb.AND
        (
            KeyValueStoreItem.expiration > datetime(1970, 1, 1),
            KeyValueStoreItem.expiration < now
        )
    )

    qo = ndb.QueryOptions(offset=0, limit=5000)
    results = existing_items.fetch(5000, options=qo)

    keys_to_delete = []
    last_item = None
    for existing_item in results:
        last_item = existing_item
        keys_to_delete.append(existing_item.key)
        deleted+=1

    if len(keys_to_delete) > 1:
        ndb.delete_multi(keys_to_delete)
    elif len(keys_to_delete) == 1:
        if not last_item is None:
            last_item.key.delete()
