@staticmethod
def get_box_settings():
	keyy = "box_settings"
	val = memcache.get(keyy)

	if val is None:

		bucket_name = os.environ.get('BUCKET_NAME',
		app_identity.get_default_gcs_bucket_name())
		bucket = '/' + bucket_name

		app_id = app_identity.get_application_id()

		filename = bucket + '/ApplicationSettings/' + "box_settings_" + app_id + ".txt"

		credsRetryParams = gcs.RetryParams(initial_delay=0.2,
		    max_delay=5.0,
		    backoff_factor=2,
		    max_retry_period=15,
		    urlfetch_timeout=30)
		gcs_file = gcs.open(filename, 'r', retry_params=credsRetryParams)

		b64_content = gcs_file.read()
		gcs_file.close()

		jaysawn = Helpers.decrypt(b64_content)
		val = jaysawn

		memcache.set(key=keyy, value=jaysawn, time=(60 * 60 * 24 * 14))

	return json.loads(val)
