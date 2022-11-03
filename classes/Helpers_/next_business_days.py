@staticmethod
def next_business_days(dt, day_cnt):
    business_day_cnt = 0
    cpy = datetime(dt.year, dt.month, dt.day)
    while not business_day_cnt == 3:
        cpy = cpy + timedelta(days=1)
        business_day_cnt += int(cpy.isoweekday() <= 5)

    return cpy.date()

