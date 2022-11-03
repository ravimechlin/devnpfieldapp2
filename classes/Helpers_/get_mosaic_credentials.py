@staticmethod
def get_mosaic_credentials():
    keyy = "mosaic_login_credentials"
    val = memcache.get(keyy)

    if val is None:
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = "/" + bucket_name
        filename = bucket + "/ApplicationSettings/mosaic_info_" + app_identity.get_application_id() + ".txt"

        credsRetryParams = gcs.RetryParams(initial_delay=0.2,
                                       max_delay=5.0,
                                       backoff_factor=2,
                                       max_retry_period=15,
                                       urlfetch_timeout=30)

        gcs_file = gcs.open(filename, 'r', retry_params=credsRetryParams)

        jayson = Helpers.decrypt(gcs_file.read().strip())
        gcs_file.close()
        creds_dict = json.loads(jayson)
        memcache.set(key=keyy, value=creds_dict, time=3600 * 60 * 24)
        val = creds_dict

    return val
