@staticmethod
def set_transaction_payout(transaction, weeks_ahead):
    now = Helpers.pacific_now()
    dt = datetime(now.year, now.month, now.day, 12, 0, 0)
    if dt.isoweekday() in [1, 2, 3, 4]:
        dt = dt + timedelta(days=-7)
    if dt.isoweekday() == 5:
        dt = dt + timedelta(days=-8)
    if dt.isoweekday() == 6:
        dt = dt + timedelta(days=-9)
    if dt.isoweekday() == 7:
        dt = dt + timedelta(days=-10)

    dt = dt + timedelta(days=7*weeks_ahead)
    transaction.effective_dt = dt
    transaction.put()
