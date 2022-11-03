def get(self, identifier, date, hour):
    custom = False
    if "|" in identifier:
        identifier = identifier.split("|")[0]
        custom = True
    breadcrumbs = []

    dt_vals = date.split("-")
    start_dt = None
    end_dt = None

    if not custom:
        if hour == "24":
            start_dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]), 0, 0, 0)
            end_dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]), 23, 59, 59)
        else:
            start_dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]), int(hour), 0, 0)
            end_dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]), int(hour), 59, 59)
    
    else:
        start_dt_vals = date.split("-")
        start_dt = datetime(int(start_dt_vals[0]), int(start_dt_vals[1]), int(start_dt_vals[2]), 0, 0, 0)
        end_dt_vals = hour.split("-")
        end_dt = datetime(int(end_dt_vals[0]), int(end_dt_vals[1]), int(end_dt_vals[2]), 23, 59, 59)

    logs = UserLocationLogItem.query(
        ndb.AND(
            UserLocationLogItem.rep_identifier == identifier,
            UserLocationLogItem.created >= start_dt,
            UserLocationLogItem.created <= end_dt
        )
    )

    logs_copy = []
    for log in logs:
        logs_copy.append({"dt": log.created, "lat": str(log.latitude), "lng": str(log.longitude), "pin_lat": str(log.pin_latitude), "pin_lng": str(log.pin_longitude), "in_bounds": log.in_bounds})
    logs_copy = Helpers.bubble_sort(logs_copy, "dt")
    for item in logs_copy:
        item["dt"] = str(item["dt"]).split(".")[0]
        breadcrumbs.append(item)

    template_values = {"breadcrumbs": json.dumps(breadcrumbs)}
    path = Helpers.get_html_path('breadcrumbs.html')
    self.response.out.write(template.render(path, template_values))
