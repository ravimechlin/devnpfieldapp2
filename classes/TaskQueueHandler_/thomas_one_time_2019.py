def thomas_one_time_2019(self):
    from datetime import datetime
    import json
    import base64
    metric_keys = ["app_stat_CD", "app_stat_R", "app_stat_CB", "app_stat_NQ", "app_stat_NI", "app_stat_AB", "app_stat_NH"]

    dt_list = []
    dt_list.append({"start": datetime(2019, 1, 1), "end": datetime(2019, 1, 31, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 2, 1), "end": datetime(2019, 2, 28, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 3, 1), "end": datetime(2019, 3, 31, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 4, 1), "end": datetime(2019, 4, 30, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 5, 1), "end": datetime(2019, 5, 31, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 6, 1), "end": datetime(2019, 6, 30, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 7, 1), "end": datetime(2019, 7, 31, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 8, 1), "end": datetime(2019, 8, 31, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 9, 1), "end": datetime(2019, 9, 30, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 10, 1), "end": datetime(2019, 10, 31, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 11, 1), "end": datetime(2019, 11, 30, 23, 59, 59)})
    dt_list.append({"start": datetime(2019, 12, 1), "end": datetime(2019, 12, 31, 23, 59, 59)})

    month_idx_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    data = []
    new_obj = {}
    for key in metric_keys:
        new_obj[key] = 0
    
    rge = dt_list[int(self.request.get("month"))]
    
    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.metric_key.IN(metric_keys),
            LeaderBoardStat.dt >= rge["start"],
            LeaderBoardStat.dt <= rge["end"]
        )
    )
    for stat in stats:
        new_obj[stat.metric_key] += 1

    data.append(new_obj)
    json_str = json.dumps(data)

    attachment_data = {}
    attachment_data["data"] = []
    attachment_data["content_types"] = []
    attachment_data["filenames"] = []

    attachment_data["data"].append(base64.b64encode(json_str))
    attachment_data["content_types"].append("application/json")
    attachment_data["filenames"].append(month_idx_names[int(self.request.get("month"))] + "_data.json")

    subject = "One Off - " + month_idx_names[int(self.request.get("month"))]
    msg_body = "See Attached..."
    Helpers.send_email("rnirnber@gmail.com", subject, msg_body, attachment_data)

