def lead_assignment_conflict_check(self):
    event = CalendarEvent.first(
        ndb.AND(
            CalendarEvent.event_key == "sp2",
            CalendarEvent.field_app_identifier == self.request.get("identifier")
        )
    )
    start_dt = datetime(1970, 1, 1)
    end_dt = datetime(1970, 1, 1, 1)
    if not event is None:
        start_dt = event.start_dt
        end_dt = event.end_dt

    self.response.content_type = "application/json"
    self.response.out.write(json.dumps(Helpers.scheduling_conflict(start_dt, end_dt, self.request.get("rep_identifier")), event.identifier))


