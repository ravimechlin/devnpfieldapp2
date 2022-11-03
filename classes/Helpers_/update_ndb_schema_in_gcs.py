@staticmethod
def update_ndb_schema_in_gcs(clsname):
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
    lines = lines.replace("\r", "")

    filename2 = bucket + '/Schemas/Additions/' + clsname + ".addition"
    gcs_file2 = gcs.open(filename2, 'r', retry_params=credsRetryParams)
    lines2 = gcs_file2.read()
    gcs_file2.close()
    lines2 = lines2.replace("\r", "")
    lines2_items = lines2.split("\n")
    lines += "\n" + lines2_items[0] + " = " + lines2_items[1] + "(required=True)"

    filename3 = bucket + "/Schemas/" + clsname + ".schema"

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file3 = gcs.open(
                        filename3,
                        'w',
                        content_type="text/plain",
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar',
                                 'x-goog-acl': 'public-read'},
                        retry_params=write_retry_params)

    gcs_file3.write(lines)
    gcs_file3.close()
    Helpers.kill_ndb_schema_cache(clsname)
    return lines2_items[0] + "|||" + lines2_items[1] + "|||" + lines2_items[2]

