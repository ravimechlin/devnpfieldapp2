@staticmethod
def string_to_datetime(in_str):
    ret_val = None
    try:
        a = datetime.strptime(in_str, '%Y-%m-%d %H:%M:%S.%f')
            #2015-07-14 08:14:01.375010
        ret_val = a
    except:
        d_items = in_str.split(" ")[0].split("-")
        t_items = in_str.split(" ")[1].split(":")

        try:
            b = datetime(int(d_items[0]), int(d_items[1]), int(d_items[2]), int(t_items[0]), int(t_items[1]), int(t_items[2].split(".")[0]), int(t_items[2].split(".")[1]))
            ret_val = b
        except:
            c = datetime(int(d_items[0]), int(d_items[1]), int(d_items[2]), int(t_items[0]), int(t_items[1]), int(t_items[2]), 0)
            ret_val = c

    return ret_val

