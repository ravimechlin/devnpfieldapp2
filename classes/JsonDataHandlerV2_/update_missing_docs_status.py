def update_missing_docs_status(self):
    from datetime import datetime

    identifier = self.request.get("identifier")
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "missing_docs_" + identifier)
    if kv is None:
        kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="missing_docs_" + identifier,
            expiration=datetime(1970, 1, 1)
        )
    kv.val = self.request.get("status")
    kv.put()
