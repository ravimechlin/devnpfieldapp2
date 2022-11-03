@staticmethod
def google_calendar_sync(fn, event, old_start_dt, old_end_dt, identifier="-1", series_id="-1"):
  if app_identity.get_application_id() in ["devnpfieldapp2", "npfieldapp"]:
    you_rl = "https://script.google.com/a/newpower.net/macros/s/AKfycbz22L6s8l2NJqzidVzih06htfWXyskjH1JHJ00jzQFnoBH9BfU/exec"
    params = {}
    params["fn"] = fn
    event.name = event.name.replace( u'\u2013', '-')
    event.description = event.description.replace( u'\u2013', '-')
    
    if "one_time" in fn:
        if not "delete" in fn:
            params["identifier"] = event.identifier
            params["name"] = event.name
            params["notes"] = event.details
            params["all_day"] = str(int(event.all_day))
            params["color"] = event.color
        else:
            params["identifier"] = identifier
            params["start_dt"] = str(old_start_dt.year) + "_" + str(old_start_dt.month) + "_" + str(old_start_dt.day) + "_" + str(old_start_dt.hour) + "_" + str(old_start_dt.minute) + "_" + str(old_start_dt.second)
            params["end_dt"] = str(old_end_dt.year) + "_" + str(old_end_dt.month) + "_" + str(old_end_dt.day) + "_" + str(old_end_dt.hour) + "_" + str(old_end_dt.minute) + "_" + str(old_end_dt.second)
        if "one_time" in fn and (not "delete" in fn):
            params["start_dt"] = str(event.start_dt.year) + "_" + str(event.start_dt.month) + "_" + str(event.start_dt.day) + "_" + str(event.start_dt.hour) + "_" + str(event.start_dt.minute) + "_" + str(event.start_dt.second)
            params["end_dt"] = str(event.end_dt.year) + "_" + str(event.end_dt.month) + "_" + str(event.end_dt.day) + "_" + str(event.end_dt.hour) + "_" + str(event.end_dt.minute) + "_" + str(event.end_dt.second)      
        if fn == "update_one_time_event":
            params["old_start_dt"] = str(old_start_dt.year) + "_" + str(old_start_dt.month) + "_" + str(old_start_dt.day) + "_" + str(old_start_dt.hour) + "_" + str(old_start_dt.minute) + "_" + str(old_start_dt.second)
            params["old_end_dt"] = str(old_end_dt.year) + "_" + str(old_end_dt.month) + "_" + str(old_end_dt.day) + "_" + str(old_end_dt.hour) + "_" + str(old_end_dt.minute) + "_" + str(old_end_dt.second)        
        
    else:
        #assume repeated events
        if fn == "create_repeated_event" or fn == "update_repeated_event":
            params["name"] = event.name;
            params["notes"] = event.details;
            params["color"] = event.color;
            params["start_hour"] = str(event.start_dt.hour)
            params["start_minute"] = str(event.start_dt.minute)
            params["end_hour"] = str(event.end_dt.hour)
            params["end_minute"] = str(event.end_dt.minute)
            params["dow"] = event.repeated_days
            params["exception_dates"] = event.exception_dates
            params["identifier"] = event.identifier
            params["google_series_id"] = event.google_series_id

        elif fn == "delete_repeated_event":
            params["google_series_id"] = series_id

    form_data = urllib.urlencode(params)

    resp = urlfetch.fetch(
        url=you_rl,
        payload=form_data,
        deadline=60 * 5,
        method=urlfetch.POST,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )


