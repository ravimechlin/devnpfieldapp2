@staticmethod
def gcs_file_exists(path):
    status = False
    if not path[0] == "/":
        path = "/" + path
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    filename = bucket + path
    retryParams = gcs.RetryParams(initial_delay=0.2,
                                    max_delay=5.0,
                                    backoff_factor=2,
                                    max_retry_period=15,
                                    urlfetch_timeout=30)

    try:
        stat = gcs.stat(filename, retry_params=None)
        status = True
    except:
        status = False
    return status

    #try:
    #    f = gcs.open(filename,'r', retry_params=retryParams)
    #    f.close()
    #    status = True
    #except:
    #    status = False
    #return status

