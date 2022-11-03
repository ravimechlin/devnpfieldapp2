@staticmethod
def jump_to_next_quarter(dt):
    today = Helpers.pacific_today()
    q1_start = date(today.year + 1, 1, 1)
    q1_start_comp = date(today.year, 1, 1)
    q2_start = date(today.year, 4, 1)
    q3_start = date(today.year, 7, 1)
    q4_start = date(today.year, 10, 1)
    if dt >= q1_start_comp and dt < q2_start:
        return q2_start
    if dt >= q2_start and dt < q3_start:
        return q3_start
    if dt >= q3_start and dt < q4_start:
        return q4_start
    return q1_start

