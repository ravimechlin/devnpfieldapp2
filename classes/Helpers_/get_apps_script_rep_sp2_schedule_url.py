@staticmethod
def get_apps_script_rep_sp2_schedule_url():
    keyy = "apps_script_url_for_rep_sp2_schedule"
    val = memcache.get(keyy)

    if val is None:
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        filename = bucket + '/ApplicationSettings/apps_script_rep_sp2_schedule.url'

        credsRetryParams = gcs.RetryParams(initial_delay=0.2,
                                       max_delay=5.0,
                                       backoff_factor=2,
                                       max_retry_period=15,
                                       urlfetch_timeout=30)

        gcs_file = gcs.open(filename, 'r', retry_params=credsRetryParams)

        apps_script_url = gcs_file.read().strip()
        gcs_file.close()
        memcache.set(key=keyy, value=apps_script_url, time=3600 * 60 * 24)
        val = apps_script_url

    return val

