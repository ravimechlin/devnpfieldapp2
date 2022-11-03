@staticmethod
def get_check_number_for_transaction(user_identifier, weeks_ahead):
    upcoming_friday = Helpers.upcoming_friday()
    upcoming_friday = upcoming_friday + timedelta(days=7*weeks_ahead)

    c_num = "-1"
    key = "check_number_for_" + user_identifier + "_" + str(upcoming_friday).split(" ")[0]
    kv_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == key)
    if not kv_item is None:
        c_num = kv_item.val

    return c_num
