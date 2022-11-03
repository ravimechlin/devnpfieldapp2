@staticmethod
def get_documentation_images(user_type, state, keys_to_exclude=[], page_idx=0):
    ret_dict = {}
    user_type_page_set = {"asst_mgr": 6, "co_mgr": 6, "field": 6, "rg_mgr": 5, "sales_dist_mgr": 6, "survey": 2}
    user_type_page_count_set = {"asst_mgr": 9, "co_mgr": 9, "field": 9, "rg_mgr": 8, "sales_dist_mgr": 9, "survey": 3}

    bucket_name = os.environ.get('BUCKET_NAME',
        app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name

    w9_image_file = bucket + '/Images/' + "W-9.jpg"
    i9_image_file = bucket + '/Images/' + "I-9.jpg"
    i9_image_file2 = bucket + '/Images/' + "I-9-2.jpg"

    agreement_signature_image_file = bucket + '/Images/' + user_type.upper() + "_" + state.upper() + "_" + str(user_type_page_set[user_type]) + ".jpg"
    credsRetryParams = gcs.RetryParams(initial_delay=0.2,
        max_delay=5.0,
        backoff_factor=2,
        max_retry_period=15,
        urlfetch_timeout=10)

    if not "w9" in keys_to_exclude:
        ret_dict["w9"] = gcs.open(w9_image_file, 'r', retry_params=credsRetryParams)
    if not "i9" in keys_to_exclude:
        ret_dict["i9"] = gcs.open(i9_image_file, 'r', retry_params=credsRetryParams)
        ret_dict["i9_2"] = gcs.open(i9_image_file2, 'r', retry_params=credsRetryParams)
    if not "agreement_signature" in keys_to_exclude:
        ret_dict["agreement_signature"] = gcs.open(agreement_signature_image_file, 'r', retry_params=credsRetryParams)
    if not "before_signature_images" in keys_to_exclude:
        ret_dict["before_signature_images"] = []
    if not "after_signature_images" in keys_to_exclude:
        ret_dict["after_signature_images"] = []

    ret_dict["signature_page_index"] = user_type_page_set[user_type]
    ret_dict["agreement_page_count"] = user_type_page_count_set[user_type]

    if not "before_signature_images" in keys_to_exclude:
        count = 1
        while count < user_type_page_set[user_type]:
            before_sig_image_file = bucket + "/Images/" + user_type.upper() + "_" + state.upper() + "_" + str(count) + ".jpg"
            if page_idx > 0 and (not page_idx == count):
                before_sig_image_file = bucket + "/Images/blank_" + str(count) + ".txt"

            f = gcs.open(before_sig_image_file, 'r', retry_params=credsRetryParams)
            ret_dict["before_signature_images"].append(f)
            count += 1

    if not "after_signature_images" in keys_to_exclude:
        count = user_type_page_set[user_type] + 1
        got_404 = False
        while not got_404:
            after_sig_image_file = bucket + "/Images/" + user_type.upper() + "_" + state.upper() + "_" + str(count) + ".jpg"

            try:
                f = gcs.open(after_sig_image_file, 'r', retry_params=credsRetryParams)
                ret_dict["after_signature_images"].append(f)
            except:
                got_404 = True

            count += 1

    return ret_dict



