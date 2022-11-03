def record_hours_knocked(self):
    from google.appengine.api import taskqueue
    from datetime import datetime, timedelta

    users = json.loads(self.request.get("users"))
    if len(users) > 0:
        user = users[0]
        now = Helpers.pacific_now()
        yesterday = now + timedelta(days=-1)
        yesterday_start = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
        yesterday_end = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

# Code was removed from here and commeted at the bottom()

        '''user_knocked = UserKnockedHours.first(UserKnockedHours.rep_identifier == user)

        hours = 0

        if user_knocked is not None:
            hours = user_knocked.knocked_hours_daily
            hours = round(hours, 0)
            hours = int(hours)

        if hours > 0:
            rep = FieldApplicationUser.first(FieldApplicationUser.identifier == user)
            if not rep is None:
                stats_to_put = []
                t = yesterday_start + timedelta(hours=12)
                cnt = 0
                while cnt < hours:
                    stat = LeaderBoardStat(
                        identifier=Helpers.guid(),
                        dt=t,
                        field_app_identifier="-1",
                        metric_key="hours_knocked",
                        office_identifier=rep.main_office,
                        rep_id=rep.rep_id,
                        in_bounds=True,
                        pin_identifier="-1"
                    )
                    stats_to_put.append(stat)
                    cnt += 1

                if len(stats_to_put) == 1:
                    stats_to_put[0].put()
                elif len(stats_to_put) > 1:
                    ndb.put_multi(stats_to_put)

        del users[0]
        taskqueue.add(url="/tq/record_hours_knocked", params={"users": json.dumps(users)})'''

        logs = UserLocationLogItem.query(
            ndb.AND(
                UserLocationLogItem.rep_identifier == user,
                UserLocationLogItem.created >= yesterday_start,
                UserLocationLogItem.created <= yesterday_end
            )
        )

        user_log_items = []

        for log in logs:
            user_log_items.append({"created": log.created, "in_bounds": log.in_bounds})
        user_log_items = Helpers.bubble_sort(user_log_items, "created")

        if len(user_log_items) > 1:

            start_idx = -1
            end_idx = -1

            cnt = 0
            for log in user_log_items:
                if log["in_bounds"] and (start_idx == -1):
                    start_idx = cnt
                if log["in_bounds"]:
                    end_idx = cnt
                cnt += 1

            dts = []
            for item in user_log_items:
                dts.append(item["created"])

            dts.sort()

            if len(dts) > 1 and (not start_idx == -1) and (not end_idx == -1):
                dts_copy = []
                for item in dts:
                    dts_copy.append(str(item))

                next_dt = dts[end_idx]
                this_dt = dts[start_idx]

                total_seconds = abs(float((next_dt - this_dt).total_seconds()))

                hours = (total_seconds / float(3600))
                hours = round(hours, 0)
                hours = int(hours)

                if hours > 0:
                    rep = FieldApplicationUser.first(FieldApplicationUser.identifier == user)
                    if not rep is None:
                        stats_to_put = []
                        t = yesterday_start + timedelta(hours=12)
                        cnt = 0
                        while cnt < hours:
                            stat = LeaderBoardStat(
                                identifier=Helpers.guid(),
                                dt=t,
                                field_app_identifier="-1",
                                metric_key="hours_knocked",
                                office_identifier=rep.main_office,
                                rep_id=rep.rep_id,
                                in_bounds=True,
                                pin_identifier="-1"
                            )
                            stats_to_put.append(stat)
                            cnt += 1

                        if len(stats_to_put) == 1:
                            stats_to_put[0].put()
                        elif len(stats_to_put) > 1:
                            ndb.put_multi(stats_to_put)

        del users[0]
        taskqueue.add(url="/tq/record_hours_knocked", params={"users": json.dumps(users)})

