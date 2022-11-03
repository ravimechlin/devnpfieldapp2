def read(self, keep_locked=False):
    key1 = "lock_for_" + self._path
    key2 = "read_lock_for_" + self._path
    vals = memcache.get_multi([key1, key2])
    keys = vals.keys()
    locked = (key1 in keys or key2 in keys)

    while locked:
        time.sleep(1)
        vals = memcache.get_multi([key1, key2])
        keys = vals.keys()
        locked = (key1 in keys or key2 in keys)

    memcache.set_multi({key1: "1", key2: "1"}, time=60)

    buff = None
    try:
        f = gcs.open(self._path, 'r', retry_params=self._retryParams)
        buff = f.read()
        f.close()
    except:
        locked = locked

    if not keep_locked:
        memcache.delete_multi([key1, key2])
    return buff
