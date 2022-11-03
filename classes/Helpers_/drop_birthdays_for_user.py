@staticmethod
def drop_birthdays_for_user(user):
    events = CalendarEvent.query(CalendarEvent.event_key == user.identifier + "_birthday")
    for event in events:    
        old_start_dt = event.start_dt
        old_end_dt = event.end_dt
        old_start_dt_str = str(old_start_dt.year) + "_" + str(old_start_dt.month) + "_" + str(old_start_dt.day) + "_" + str(old_start_dt.hour) + "_" + str(old_start_dt.minute) + "_" + str(old_start_dt.second)
        old_end_dt_str = str(old_end_dt.year) + "_" + str(old_end_dt.month) + "_" + str(old_end_dt.day) + "_" + str(old_end_dt.hour) + "_" + str(old_end_dt.minute) + "_" + str(old_end_dt.second)

        event.key.delete()
        from google.appengine.api import taskqueue
        taskqueue.add(url="/tq/google_calendar", params={"fn": "delete_one_time_event", "identifier": event.identifier, "old_start_dt": old_start_dt_str, "old_end_dt": old_end_dt_str})

