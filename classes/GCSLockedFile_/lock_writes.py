@staticmethod
def lock_writes(paths):
    dct = {}
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    for path in paths:
        if not path[0] == "/":
            path = "/" + path
            
        filename = bucket + path
        dct["write_lock_for_" + filename] = "1"
    memcache.set_multi(dct, time=60)
