@staticmethod
def check_registration_keycode(code, mgr_key):
	keyy = "reg_mgr_codes"
	val = memcache.get(keyy)
	
	answer = False
	
	codes = None
	if val is None:
		
		bucket_name = os.environ.get('BUCKET_NAME',
			app_identity.get_default_gcs_bucket_name())
		bucket = '/' + bucket_name
	
		app_id = app_identity.get_application_id()
	
		filename = bucket + '/ApplicationSettings/' + "reg_mgr_" + app_id + ".json"
		credsRetryParams = gcs.RetryParams(initial_delay=0.2,
			max_delay=5.0,
			backoff_factor=2,
			max_retry_period=15,
			urlfetch_timeout=30)
		gcs_file = gcs.open(filename, 'r', retry_params=credsRetryParams)
		json_txt = gcs_file.read()
		memcache.set(key=keyy, value=json_txt, time=(60 * 60 * 24 * 14))
		gcs_file.close()
		codes = json.loads(json_txt)
		
	else:
		codes = json.loads(val);
		
	if mgr_key in codes.keys():
		answer = (codes[mgr_key] == code)
		
	return answer
	

