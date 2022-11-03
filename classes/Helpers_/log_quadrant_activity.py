@staticmethod
def log_quadrant_activity(msg):
    today = Helpers.pacific_today()
    now = Helpers.pacific_now()
    one_week_from_now = now + timedelta(hours=24 * 7)
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "area_activity_" + str(today))
    if kv is None:
        kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="area_activity_" + str(today),
            val="[]",
            expiration=one_week_from_now
        )
    values = json.loads(kv.val)
    values.append({"msg": msg, "dt": str(now).split(".")[0]})
    kv.val = json.dumps(values)
    kv.put()
