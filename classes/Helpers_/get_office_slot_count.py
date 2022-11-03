@staticmethod
def get_office_slot_count(office_num):
    slot_counts = {"1": 6, "2": 6, "3": 5, "4": 4}
    return slot_counts[str(office_num)]

