@staticmethod
def bubble_sort(lst, key):
    import copy
    if len(lst) < 1:
        return lst

    #no need to sort

    is_dict = (str(type(lst[0])) == "<type 'dict'>")
    if is_dict:
        pred_fn = lambda a, b, k: a[k] > b[k]
    else:
        pred_fn = lambda a, b, k: getattr(a, k, 0) > getattr(b, k, 0)

    length = len(lst)
    idx = 0

    while idx < length - 1:
        item_a = lst[idx]
        item_b = lst[idx + 1]


        if pred_fn(item_a, item_b, key):
            item_aa = copy.deepcopy(item_a)
            item_bb = copy.deepcopy(item_b)

            lst[idx] = item_bb
            lst[idx + 1] = item_aa

            idx = -1

        idx += 1

    return lst
