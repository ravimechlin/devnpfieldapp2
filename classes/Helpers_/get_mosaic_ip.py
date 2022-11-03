@staticmethod
def get_mosaic_ip():
    keyy = "mosaic_ip_address"
    val = memcache.get(keyy)

    if val is None:
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = "/" + bucket_name
        filename = bucket + "/ApplicationSettings/mosaic_vm.txt"

        credsRetryParams = gcs.RetryParams(initial_delay=0.2,
                                       max_delay=5.0,
                                       backoff_factor=2,
                                       max_retry_period=15,
                                       urlfetch_timeout=30)

        gcs_file = gcs.open(filename, 'r', retry_params=credsRetryParams)

        ip = gcs_file.read().strip()
        gcs_file.close()
        memcache.set(key=keyy, value=ip, time=3600 * 60 * 24)
        val = ip

    return val
