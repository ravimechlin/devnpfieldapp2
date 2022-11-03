@staticmethod
def get_ndb_class_definition_lines(clsname):

    keyy = "definition_for_" + clsname

    val = memcache.get(keyy)
    lines = None

    if val is None:

        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        filename = bucket + '/Schemas/' + clsname + '.schema'

        credsRetryParams = gcs.RetryParams(initial_delay=0.2,
                                       max_delay=5.0,
                                       backoff_factor=2,
                                       max_retry_period=15,
                                       urlfetch_timeout=30)

        gcs_file = gcs.open(filename, 'r', retry_params=credsRetryParams)

        lines = gcs_file.read()
        gcs_file.close()

        lines += "\n"

        try:
            filename2 = bucket + '/Methods/' + clsname + '.methods'
            gcs_file2 = gcs.open(filename2, 'r', retry_params=credsRetryParams)
            lines += gcs_file2.read()
            gcs_file2.close()
        except:
            lines = lines

        memcache.set(key=keyy, value=lines, time=3600 * 60 * 24)
    else:
        lines = val

    return lines.replace("\r", "").split("\n")

