@staticmethod
def pacific_last_friday(days_behind=0):
    now = Helpers.pacific_now()
    if not days_behind == 0:
        now = now + timedelta(days=-1 * days_behind)
    if (now.isoweekday() == 5) and (now.hour == 0) and (now.minute == 0) and (now.second == 0):
        return datetime(now.year, now.month, now.day, 0, 0, 0) + timedelta(days=-7)

    last_friday = now
    wd = last_friday.isoweekday()
    sub_count = 0
    while not (wd == 5):
        last_friday = last_friday + timedelta(days=-1)
        wd = last_friday.isoweekday()
        sub_count += 1

    if sub_count == 0:
        last_friday = last_friday + timedelta(days=-7)

    return datetime(last_friday.year, last_friday.month, last_friday.day, 0, 0, 0)
