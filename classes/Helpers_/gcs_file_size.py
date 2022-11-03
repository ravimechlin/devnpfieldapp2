@staticmethod
def gcs_file_size(path):
    size = 1024 * 1024 * 1024
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
        size = stat.st_size
    except:
        size = size
    return size

    #try:
    #    f = gcs.open(filename,'r', retry_params=retryParams)
    #    f.close()
    #    status = True
    #except:
    #    status = False
    #return status

