@staticmethod
def unlock_reads(paths):
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    lst = []
    for path in paths:
        if not path[0] == "/":
            path = "/" + path
        filename = bucket + path
        lst.append("read_lock_for_" + filename)
    memcache.delete_multi(lst)
