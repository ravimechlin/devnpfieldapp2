@staticmethod
def data_dict_to_url_params(dct):
    import urllib
    ret_str = "?"
    cnt = 0
    length = len(dct.keys())
    if len == 0:
        return ""

    for item in dct.keys():
        ret_str += (item + "=" + urllib.quote(dct[item], safe='~()*!.\''))
        if not (cnt == (length - 1)):
            ret_str += "&"
        cnt += 1

    return ret_str

