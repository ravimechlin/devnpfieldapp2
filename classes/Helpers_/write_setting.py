@staticmethod
def write_setting(setting_key, setting_value):
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    filename = bucket + '/ApplicationSettings/miscellaneous_settings_' + app_identity.get_application_id() + '.json'

    retryParameters = gcs.RetryParams(initial_delay=0.2,
                                               max_delay=5.0,
                                               backoff_factor=2,
                                               max_retry_period=15,
                                               urlfetch_timeout=30)

    gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
    jaysawn = gcs_file.read()
    gcs_file.close()

    settings = json.loads(jaysawn)
    settings[setting_key] = setting_value

    jaysawn2 = json.dumps(settings)

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)

    gcs_file = gcs.open(
                        filename,
                        'w',
                        content_type="text/plain",
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar',
                                 'x-goog-acl': 'public-read'},
                        retry_params=write_retry_params
    )
    gcs_file.write(jaysawn2)
    gcs_file.close()

    keyy = "miscellaneous_application_settings"
    memcache.delete(keyy)
    return
