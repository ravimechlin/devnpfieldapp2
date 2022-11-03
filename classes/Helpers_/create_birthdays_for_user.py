@staticmethod
def create_birthdays_for_user(user):
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "user_dob_" + user.identifier)
    if not kv is None:
        dt_vals = kv.val.split("-")
        if not (int(dt_vals[0]) == 2 and int(dt_vals[1]) == 29):
            dts = []
            cnt = 0
            year_offset = 0
            while cnt < 10:
                dt = datetime(Helpers.pacific_now().year + year_offset, int(dt_vals[0]), int(dt_vals[1]))
                dts.append(dt)
                year_offset += 1
                cnt += 1

            for dt2 in dts:
                event = CalendarEvent(
                    identifier=Helpers.guid(),
                    field_app_identifier="-1",
                    name=user.first_name + " " + user.last_name + "'s Birthday",
                    all_day=False,
                    calendar_key="main",
                    event_key=user.identifier + "_birthday",
                    repeated=False,
                    repeated_days="[]",
                    details="Happy Birthday!",
                    color="yellow",
                    exception_dates="[]",
                    google_series_id="-1",
                    owners=json.dumps(["-1"]),
                    start_dt=datetime(dt2.year, dt2.month, dt2.day, 12, 0, 0),
                    end_dt=datetime(dt2.year, dt2.month, dt2.day, 13, 0, 0)
                )
                event.put()
                from google.appengine.api import taskqueue
                taskqueue.add(url="/tq/google_calendar", params={"identifier": event.identifier, "fn": "create_one_time_event"})
