def sales_form_sp2_scheduling_conflict(self):
    from datetime import datetime
    from datetime import timedelta

    date_vals = self.request.get("sp2_date").split("-")
    hours = int(self.request.get("sp2_hours"))
    mins = int(self.request.get("sp2_mins"))
    pm = (self.request.get("pm") == "1")
    if pm and (not hours == 12):
        hours += 12

    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("field_app_identifier"))
    minutes_off = Helpers.get_sp2_special_offset(app_entry.office_identifier)

    start_dt = datetime(int(date_vals[2]), int(date_vals[0]), int(date_vals[1]), hours, mins, 0)
    end_dt = start_dt + timedelta(minutes=119 - minutes_off)

    self.response.content_type = "application/json"
    self.response.out.write(json.dumps(Helpers.scheduling_conflict(start_dt, end_dt, self.request.get("identifier"))))
