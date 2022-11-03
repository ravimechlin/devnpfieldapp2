def google_calendar(self):
    return
    if self.request.get("fn") == "create_one_time_event":
        event = CalendarEvent.first(CalendarEvent.identifier == self.request.get("identifier"))
        if not event is None:
            Helpers.google_calendar_sync("create_one_time_event", event, Helpers.pacific_now(), Helpers.pacific_now())

    elif self.request.get("fn") == "update_one_time_event":
        event = CalendarEvent.first(CalendarEvent.identifier == self.request.get("identifier"))
        if not event is None:
            old_start_dt_vals = self.request.get("old_start_dt").split("_")
            old_end_dt_vals = self.request.get("old_end_dt").split("_")
            old_start_dt = datetime(
                int(old_start_dt_vals[0]),
                int(old_start_dt_vals[1]),
                int(old_start_dt_vals[2]),
                int(old_start_dt_vals[3]),
                int(old_start_dt_vals[4]),
                int(old_start_dt_vals[5])
            )
            old_end_dt = datetime(
                int(old_end_dt_vals[0]),
                int(old_end_dt_vals[1]),
                int(old_end_dt_vals[2]),
                int(old_end_dt_vals[3]),
                int(old_end_dt_vals[4]),
                int(old_end_dt_vals[5])
            )

            Helpers.google_calendar_sync("create_one_time_event", event, Helpers.pacific_now(), Helpers.pacific_now())

    elif self.request.get("fn") == "delete_one_time_event":
        old_start_dt_vals = self.request.get("old_start_dt").split("_")
        old_end_dt_vals = self.request.get("old_end_dt").split("_")
        old_start_dt = datetime(
            int(old_start_dt_vals[0]),
            int(old_start_dt_vals[1]),
            int(old_start_dt_vals[2]),
            int(old_start_dt_vals[3]),
            int(old_start_dt_vals[4]),
            int(old_start_dt_vals[5])
        )
        old_end_dt = datetime(
            int(old_end_dt_vals[0]),
            int(old_end_dt_vals[1]),
            int(old_end_dt_vals[2]),
            int(old_end_dt_vals[3]),
            int(old_end_dt_vals[4]),
            int(old_end_dt_vals[5])
        )
        Helpers.google_calendar_sync("delete_one_time_event", None, old_start_dt, old_end_dt, self.request.get("identifier"))

    elif self.request.get("fn") == "create_repeated_event":
        event = CalendarEvent.first(CalendarEvent.identifier == self.request.get("identifier"))
        if not event is None:
            Helpers.google_calendar_sync("create_repeated_event", event, Helpers.pacific_now(), Helpers.pacific_now())

    elif self.request.get("fn") == "delete_repeated_event":
        Helpers.google_calendar_sync("delete_repeated_event", None, Helpers.pacific_now(), Helpers.pacific_now(), "-1", self.request.get("google_series_id"))

    elif self.request.get("fn") == "update_repeated_event":
        event = CalendarEvent.first(CalendarEvent.identifier == self.request.get("identifier"))
        if not event is None:
            Helpers.google_calendar_sync("update_repeated_event", event, Helpers.pacific_now(), Helpers.pacific_now())

