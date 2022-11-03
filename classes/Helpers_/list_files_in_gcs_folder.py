@staticmethod
def list_files_in_gcs_folder(path, ext=None):
    ret = []
    if not path[0] == "/":
        path = "/" + path
    if path[len(path) - 1] == "/":
        path = path[0:len(path) - 1]

    orig_path = path
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    filename = bucket + path
    path = filename

    stats = gcs.listbucket(path, max_keys=1000)
    for stat in stats:
        if ext is None:
            fname = stat.filename.replace("/" + bucket_name, "").replace(orig_path, "")
            ret.append(fname[1:])
        else:
            split_vals = stat.filename.replace("/" + bucket_name, "").split(".")
            last = split_vals[len(split_vals) - 1]
            if ext == last:
                fname = stat.filename.replace("/" + bucket_name, "").replace(orig_path, "")
                ret.append(fname[1:])
    return ret

