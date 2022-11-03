def leaderboard_notifications(self):
    from datetime import datetime
    from datetime import timedelta
    import hashlib
    ten_minutes_ago = Helpers.pacific_now() + timedelta(minutes=-10)
    
    self.response.content_type = "application/json"
    ret_json = {"notifications": []}

    stats = LeaderBoardStat.query(LeaderBoardStat.dt >= ten_minutes_ago)
    for stat in stats:
        if stat.metric_key == "packets_submitted":
            hashed = hashlib.md5(self.request.get("identifier") + "_" + stat.identifier).hexdigest().lower()
            kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "notification_" + hashed)
            if kv is None:
                kv = KeyValueStoreItem(
                    identifier=Helpers.guid(),
                    keyy="notification_" + hashed,
                    val="1",
                    expiration=ten_minutes_ago + timedelta(minutes=30)
                )
                kv.put()
                rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == stat.rep_id)
                if not rep is None:
                    ret_json["notifications"].append({"name": rep.first_name.strip().title() + " " + rep.last_name.strip().title(), "identifier": stat.identifier})

    self.response.out.write(json.dumps(ret_json))

