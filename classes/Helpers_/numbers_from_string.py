@staticmethod
def numbers_from_str(in_str):
    allowed = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    ret_str = ""
    for item in in_str:
        if item in allowed:
            ret_str += item

    return ret_str

