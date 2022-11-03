def record_hours_knocked_v2(self):
    from datetime import datetime
    from datetime import timedelta
    from google.appengine.api import taskqueue
    import json

    now = Helpers.pacific_now()
    yesterday = now + timedelta(days=-1)
    yesterday_start = datetime(yesterday.year, yesterday.month, yesterday.day)
    yesterday_end = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

    users = json.loads(self.request.get("users"))
    if len(users) > 0:
        identifier = users[0]
        user = FieldApplicationUser.first(FieldApplicationUser.identifier == identifier)
        if not user is None:
            stats_to_put = []
            kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "clock_ins_clock_outs_" + str(yesterday.date()) + "_" + identifier)
            if not kv is None:
                items = json.loads(kv.val)            
                if len(items) > 0:
                    last_item = items[len(items) - 1]
                    if last_item["status"] == "in":
                        location_logs = UserLocationLogItem.query(
                            ndb.AND(
                                UserLocationLogItem.rep_identifier == identifier,
                                UserLocationLogItem.created >= yesterday_start,
                                UserLocationLogItem.created <= yesterday_end
                            )
                        )
                        cpy = []
                        for log in location_logs:
                            if log.in_bounds and (log.latitude < 400.0):
                                cpy.append(log)
                        cpy = Helpers.bubble_sort(cpy, "created")
                        cpy.reverse()
                        if len(cpy) > 0:
                            # old code
                            #items.append({"status": "out", "dt": str(cpy[0].dt).split(".")[0]})
                            
                            #code changed on 10/22/@10:40pm
                            items.append({"status": "out", "dt": str(cpy[0].created).split(".")[0]})
                        else:
                            last_item2 = json.loads(json.dumps(items[len(items) - 1]))
                            last_item2["status"] = "out"
                            items.append(last_item2)

                    done = False
                    cnt = 0
                    total_seconds = float(0)
                    while not done:
                        start_dt_str = None
                        end_dt_str = None

                        try:
                            start_dt_str = items[cnt]["dt"]
                        except:
                            start_dt_str = None

                        try:
                            end_dt_str = items[cnt + 1]["dt"]
                        except:
                            end_dt_str = None

                        if (not start_dt_str is None) and (not end_dt_str is None):                            
                            start_dt_vals = start_dt_str.split(" ")[0].split("-")
                            start_dt_time_vals = start_dt_str.split(" ")[1].split(":")
                            end_dt_vals = end_dt_str.split(" ")[0].split("-")
                            end_dt_time_vals = end_dt_str.split(" ")[1].split(":")

                            floor = datetime(int(start_dt_vals[0]), int(start_dt_vals[1]), int(start_dt_vals[2]), int(start_dt_time_vals[0]), int(start_dt_time_vals[1]), int(start_dt_time_vals[2]))
                            ceiling = datetime(int(end_dt_vals[0]), int(end_dt_vals[1]), int(end_dt_vals[2]), int(end_dt_time_vals[0]), int(end_dt_time_vals[1]), int(end_dt_time_vals[2]))

                            logs_within = UserLocationLogItem.query(
                                ndb.AND(
                                    UserLocationLogItem.rep_identifier == identifier,
                                    UserLocationLogItem.created >= floor,
                                    UserLocationLogItem.created <= ceiling
                                )
                            )
                            log_tally = 0
                            for l in logs_within:
                                log_tally += int(l.in_bounds and l.latitude < 400.0)

                            if log_tally > 0:
                                total_seconds += (ceiling - floor).total_seconds()

                        #used to be one
                        #changed to two
                        cnt += 2

                        done = (start_dt_str is None) or (end_dt_str is None)

                    minutes = total_seconds / float(60)
                    minutes_rounded = round(minutes, 0)
                    minutes_int = int(minutes_rounded)

                    if minutes_int > 0:
                        hk_recording = HKTally(
                            identifier=Helpers.guid(),
                            minutes=minutes_int,
                            rep_identifier=user.identifier,
                            dt=datetime(yesterday.year, yesterday.month, yesterday.day, 12, 0, 0)                        
                        )
                        hk_recording.put()

                    hours = minutes / float(60)
                    hours = round(hours, 0)
                    hours = int(hours)
                    cnt2 = 0
                    while cnt2 < hours:
                        stat = LeaderBoardStat(
                            identifier=Helpers.guid(),
                            dt=datetime(yesterday.year, yesterday.month, yesterday.day, 12, 0, 0),
                            field_app_identifier="-1",
                            metric_key="hours_knocked_v2",
                            office_identifier=user.main_office,
                            rep_id=user.rep_id,
                            in_bounds=True,
                            pin_identifier="-1"
                        )
                        stats_to_put.append(stat)
                        cnt2 += 1

            if len(stats_to_put) == 1:
                stats_to_put[0].put()
            elif len(stats_to_put) > 1:
                ndb.put_multi(stats_to_put)

        del users[0]
        taskqueue.add(url="/tq/record_hours_knocked_v2", params={"users": json.dumps(users)})
