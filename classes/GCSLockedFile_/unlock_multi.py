@staticmethod
def unlock_multi(paths):
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    for path in paths:
        if not path[0] == "/":
            path = "/" + path
            
        filename = bucket + path
        memcache.delete("lock_for_" + filename)
