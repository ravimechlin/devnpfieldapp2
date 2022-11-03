@staticmethod
def list_payscales():
    keyy = "list_of_payscales"
    val = memcache.get(keyy)

    payscales = []
    if val is None:
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        filename = bucket + '/ApplicationSettings/payscales_' + app_identity.get_application_id() + '.json'

        retryParameters = gcs.RetryParams(initial_delay=0.2,
                                       max_delay=5.0,
                                       backoff_factor=2,
                                       max_retry_period=15,
                                       urlfetch_timeout=30)

        gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
        jaysawn = gcs_file.read()
        gcs_file.close()

        val = jaysawn

        memcache.set(key=keyy, value=jaysawn, time=(60 * 60 * 24 * 14))

    return json.loads(val)

