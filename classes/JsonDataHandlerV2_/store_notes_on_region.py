def store_notes_on_region(self):
    from datetime import datetime
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "quadrant_notes_" + self.request.get("identifier"))
    if kv is None:
        kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="quadrant_notes_" + self.request.get("identifier"),
            expiration=datetime(1970, 1, 1)
        )
    kv.val = self.request.get("notes")
    kv.put()
