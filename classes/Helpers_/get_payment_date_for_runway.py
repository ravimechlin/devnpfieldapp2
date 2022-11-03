@staticmethod
def get_payment_date_for_runway():
    ret = None
    now = Helpers.pacific_now()
    if now.isoweekday() == 1:
        ret = now + timedelta(days=11)
    elif now.isoweekday() == 2:
        ret = now + timedelta(days=10)
    elif now.isoweekday() == 3:
        ret = now + timedelta(days=9)
    elif now.isoweekday() == 4:
        ret = now + timedelta(days=8)
    elif now.isoweekday() == 5:
        ret = now + timedelta(days=7)
    elif now.isoweekday() == 6:
        ret = now + timedelta(days=6)
    elif now.isoweekday() == 7:
        ret = now + timedelta(days=12)

    return ret.date()
