@staticmethod
def get_multi(keys, file_path, type_sig_obj=None, default_value=None, cache_depth_level=1):
    if len(keys) == 0 or (cache_depth_level < 1 or cache_depth_level > 2):
        return []

    ret_vals = []

    if cache_depth_level == 1:
        vals_dict = memcache.get_multi(keys)
        for key in keys:
            if key in vals_dict.keys():
                ret_vals.append(vals_dict[key])
            else:
                ret_vals.append(None)

    elif cache_depth_level == 2:
        vals_dict = memcache.get_multi(keys)
        for key in keys:
            if key in vals_dict.keys():
                ret_vals.append(vals_dict[key])
            else:
                ret_vals.append(None)

        keys_to_query = ["-1"]
        idx = 0
        for key in keys:
            if ret_vals[idx] is None:
                keys_to_query.append(key)
            idx += 1

        kv_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(keys_to_query))
        for kv_item in kv_items:
            try:
                idx = keys.index(kv_item.keyy)
                ret_vals[idx] = kv_item.val
            except:
                logging.info("indexing issue on get_multi method for UniformCacheLayer")

    cnt = 0
    while cnt < len(ret_vals):
        val = ret_vals[cnt]
        if (not type_sig_obj is None) and (not val is None):
            if str(type(type_sig_obj)) == "<type 'int'>":
                val = int(val)

        if val is None and (not default_value is None):
            val = default_value

        ret_vals[cnt] = val
        cnt += 1

    return ret_vals







