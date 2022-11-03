@staticmethod
def gcs_copy(source_path, target_path, content_type, acl):
    if not source_path[0] == "/":
        source_path = "/" + source_path

    if not target_path[0] == "/":
        target_path = "/" + target_path

    bucket_name = os.environ.get('BUCKET_NAME',
                                 app_identity.get_default_gcs_bucket_name())

    bucket = '/' + bucket_name
    filename = bucket + source_path

    retryParameters = gcs.RetryParams(initial_delay=0.2,
                                      max_delay=5.0,
                                      backoff_factor=2,
                                      max_retry_period=15,
                                      urlfetch_timeout=30)

    gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
    source_content = gcs_file.read()


    filename2 = bucket + target_path
    try:
        gcs.delete(filename2)
    except:
        bucket = bucket

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)

    gcs_file2 = gcs.open(
        filename2,
        'w',
        content_type=content_type,
        options={'x-goog-meta-foo': 'foo',
                 'x-goog-meta-bar': 'bar',
                 'x-goog-acl': acl},
        retry_params=write_retry_params)

    gcs_file2.write(source_content)
    gcs_file.close()
    gcs_file2.close()

