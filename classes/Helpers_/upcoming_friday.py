@staticmethod
def upcoming_friday():
    hpt = Helpers.pacific_today()
    this_upcoming_friday = datetime(hpt.year, hpt.month, hpt.day, 0, 0, 1)
    weekday = this_upcoming_friday.isoweekday()

    while (not weekday == 5):
        this_upcoming_friday = this_upcoming_friday + timedelta(days=1)
        weekday = this_upcoming_friday.isoweekday()

    return this_upcoming_friday
