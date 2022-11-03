@staticmethod
def set_commission_payout(transaction):
    now = Helpers.pacific_now()
    dt = datetime(now.year, now.month, now.day, 12, 0, 0)
    if dt.isoweekday() == 5:
        dt = dt + timedelta(days=-1)
    transaction.effective_dt = dt
    transaction.put()
