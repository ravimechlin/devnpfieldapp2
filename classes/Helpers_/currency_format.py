@staticmethod
def currency_format(amt):
    if str(type(amt)) == "<type 'str'>":
        amt = float(amt)
    elif str(type(amt)) == "<type 'unicode'>":
        amt = float(amt)

    negative = False
    ret_str = str(round(amt, 2))
    if "-" in ret_str:
        ret_str = str(round(amt, 2) * -1.0)
        negative = True

    if len(ret_str.split(".")[1]) == 1:
        ret_str += "0"

    split_vals = ret_str.split(".")
    if len(split_vals[0]) == 4:
        ret_str = split_vals[0][0] + "," + split_vals[0][1] + split_vals[0][2] + split_vals[0][3]
    elif len(split_vals[0]) == 5:
        ret_str = split_vals[0][0] + split_vals[0][1] + "," + split_vals[0][2] + split_vals[0][3] + split_vals[0][4]

    elif len(split_vals[0]) == 6:
        ret_str = split_vals[0][0] + split_vals[0][1] + split_vals[0][2] + "," + split_vals[0][3] + split_vals[0][4] + split_vals[0][5]

    elif len(split_vals[0]) == 7:
        ret_str = split_vals[0][0] + "," + split_vals[0][1] + split_vals[0][2] + split_vals[0][3] + "," + split_vals[0][4] + split_vals[0][5] + split_vals[0][6]

    elif len(split_vals[0]) == 8:
        ret_str = split_vals[0][0] + split_vals[0][1] + "," + split_vals[0][2] + split_vals[0][3] + split_vals[0][4] + "," + split_vals[0][5] + split_vals[0][6] + split_vals[0][7]

    elif len(split_vals[0]) == 9:
        ret_str = split_vals[0][0] + split_vals[0][1] + split_vals[0][2] + "," + split_vals[0][3] + split_vals[0][4] + split_vals[0][5] + "," + split_vals[0][6] + split_vals[0][7] + split_vals[0][8]
    else:
        ret_str = split_vals[0]

    ret_str += ("." + split_vals[1])
    prefix = "$"
    if negative:
        prefix = "-$"

    return prefix + ret_str

