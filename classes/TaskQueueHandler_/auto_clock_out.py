def auto_clock_out(self):
    import json
    from datetime import timedelta
    from datetime import datetime

    now = Helpers.pacific_now()
    last_hour = now + timedelta(hours=-1)
    today = now.date()

    user_identifiers_to_query = ["-1"]
    users = FieldApplicationUser.query(FieldApplicationUser.current_status == 0)
    for user in users:
        logs = UserLocationLogItem.query(
            ndb.AND(
                    UserLocationLogItem.rep_identifier == user.identifier,
                    UserLocationLogItem.created >= last_hour
            )
        )
        l_cpy = []
        for l in logs:
            if l.in_bounds:
                l_cpy.append(l)

        if len(l_cpy) == 0:
            kv =  KeyValueStoreItem.first(KeyValueStoreItem.keyy == "clock_ins_clock_outs_" + str(today) + "_" + user.identifier)
            if not kv is None:
                items = json.loads(kv.val)
                last_item = items[len(items) - 1]
                if last_item["status"] == "in":
                    dt = now
                    clock_in_dt_vals = last_item["dt"].split(" ")
                    clock_in_date_vals = clock_in_dt_vals[0].split("-")
                    clock_in_time_vals = clock_in_dt_vals[1].split(":")
                    on_or_after_dt = datetime(int(clock_in_date_vals[0]), int(clock_in_date_vals[1]), int(clock_in_date_vals[2]), int(clock_in_time_vals[0]), int(clock_in_time_vals[1]), int(clock_in_time_vals[2]))


                    last_logs = UserLocationLogItem.query(
                        ndb.AND
                        (
                            UserLocationLogItem.rep_identifier == user.identifier,
                            UserLocationLogItem.created >= on_or_after_dt
                        )
                    )
                    last_logs_cpy = []
                    for log in last_logs:
                        if log.in_bounds:
                            last_logs_cpy.append(log)

                    if len(last_logs_cpy) > 0:
                        last_logs = Helpers.bubble_sort(last_logs_cpy, "created")
                        last_logs.reverse()
                        dt = last_logs[0].created

                    items.append({"status": "out", "dt": str(dt).split(".")[0], "auto": 1})

                kv2 =  KeyValueStoreItem.first(KeyValueStoreItem.keyy == "clock_ins_clock_outs_" + str(today) + "_" + user.identifier)
                if not kv2 is None:
                    items2 = json.loads(kv2.val)
                    last_item2 = items2[len(items2) - 1]
                    if last_item2["status"] == "in":
                        kv.val = json.dumps(items)
                        kv.put()
