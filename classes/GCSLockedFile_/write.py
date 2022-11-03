def write(self, data, c_type, a_see_el="public-read"):
    orig_data = ""
    if hasattr(data, "encode"):
        try:
            orig_data = data
            data = data.encode("utf-8")
        except:
            data = orig_data
    key1 = "lock_for_" + self._path
    key2 = "write_lock_for_" + self._path
    vals = memcache.get_multi([key1, key2])
    keys = vals.keys()
    locked = (key1 in keys or key2 in keys)    

    while locked:
        time.sleep(1)
        vals = memcache.get_multi([key1, key2])
        keys = vals.keys()
        locked = (key1 in keys or key2 in keys)

    memcache.set_multi({key1: "1", key2: "1"}, time=60)

    if 5 == 5:
        f = gcs.open(self._path, 'w', content_type=c_type, options={'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar', 'x-goog-acl': a_see_el, 'cache-control': 'no-cache'}, retry_params=self._write_retry_params)
        f.write(data)
        f.close()
    else:
        Helpers.send_email("rnirnber@gmail.com", "Code Issue", "Hey ray, we're getting an exception thrown when we try to write files. Can you help?")
        locked = locked

    memcache.delete_multi([key1, key2])
