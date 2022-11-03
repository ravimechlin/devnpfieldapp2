@staticmethod
def get_sales_rabbit_settings():
    keyy = "sales_rabit_settings"
    val = memcache.get(keyy)

    if val is None:

        bucket_name = os.environ.get('BUCKET_NAME',
	    app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name

	    app_id = app_identity.get_application_id()

	    filename = bucket + '/ApplicationSettings/' + "sales_rabbit_settings_" + app_id + ".json"
	    credsRetryParams = gcs.RetryParams(initial_delay=0.2,
		    max_delay=5.0,
		    backoff_factor=2,
		    max_retry_period=15,
		    urlfetch_timeout=30)
	    gcs_file = gcs.open(filename, 'r', retry_params=credsRetryParams)
	    jaysawn = gcs_file.read()
	    gcs_file.close()

        val = jaysawn

        memcache.set(key=keyy, value=jaysawn, time=(60 * 60 * 24 * 14))

    return json.loads(val)
