@staticmethod
def list_funds(rep_qualifier=False, customer_state=None):
    if not customer_state is None:
        customer_state = customer_state.lower()

    keyy = "list_of_funding_source_names"
    val = memcache.get(keyy)

    if not rep_qualifier:
        ret_list = [{"value": "n/a", "value_friendly": "N/A"}]

        if val is None:

            bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
            bucket = '/' + bucket_name
            filename = bucket + '/ApplicationSettings/funding_sources_' + app_identity.get_application_id() + '.json'

            retryParameters = gcs.RetryParams(initial_delay=0.2,
                                           max_delay=5.0,
                                           backoff_factor=2,
                                           max_retry_period=15,
                                           urlfetch_timeout=30)

            gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
            jaysawn = gcs_file.read()
            source_list = json.loads(jaysawn)
            for source in source_list:
                if not "apr" in source.keys():
                    source["apr"] = 0

            jaysawn = json.dumps(source_list)

            memcache.set(key=keyy, value=jaysawn, time=(60 * 60 * 24 * 14))
            gcs_file.close()

            for source in source_list:
                ret_list.append(source)

        else:
            sources = json.loads(val)

            for source in sources:
                ret_list.append(source)

        ret_list.append({"value": "fail", "value_friendly": "Failed Credit Check"})

    else:
        ret_list = []
        if val is None:
            tmp_list = []
            bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
            bucket = '/' + bucket_name
            filename = bucket + '/ApplicationSettings/funding_sources_' + app_identity.get_application_id() + '.json'

            retryParameters = gcs.RetryParams(initial_delay=0.2,
                                           max_delay=5.0,
                                           backoff_factor=2,
                                           max_retry_period=15,
                                           urlfetch_timeout=30)

            gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
            jaysawn = gcs_file.read()
            tmp_list = json.loads(jaysawn)
            memcache.set(key=keyy, value=jaysawn, time=(60 * 60 * 24 * 14))
            gcs_file.close()

        else:
            ret_list = json.loads(val)

        cpy2 = []
        for item in ret_list:
            if "active" in item.keys():
                if item["active"]:
                    cpy2.append(item)
        ret_list = cpy2
    return ret_list
