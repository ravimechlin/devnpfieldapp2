@staticmethod
def list_funding_groups():
    keyy = "list_of_funding_groups"
    val = memcache.get(keyy)

    ret_obj = {}
    ret_obj["group_names"] = [{"value": "unassigned", "value_friendly": "Unassigned"}]
    ret_obj["group_items"] = {"unassigned": []}

    if val == None:
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        filename = bucket + '/ApplicationSettings/funding_groups_' + app_identity.get_application_id() + '.json'

        retryParameters = gcs.RetryParams(initial_delay=0.2,
                                       max_delay=5.0,
                                       backoff_factor=2,
                                       max_retry_period=15,
                                       urlfetch_timeout=30)

        gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
        jaysawn = gcs_file.read()
        group_info = json.loads(jaysawn)

        memcache.set(key=keyy, value=jaysawn, time=(60 * 60 * 24 * 14))
        gcs_file.close()

        for group_name in group_info["group_names"]:
            ret_obj["group_names"].append(group_name)

        for group_item_key in group_info["group_items"].keys():
            ret_obj["group_items"][group_item_key] = group_info["group_items"][group_item_key]

    else:
        group_info = json.loads(val)

        for group_name in group_info["group_names"]:
            ret_obj["group_names"].append(group_name)

        for group_item_key in group_info["group_items"].keys():
            ret_obj["group_items"][group_item_key] = group_info["group_items"][group_item_key]

    return ret_obj
