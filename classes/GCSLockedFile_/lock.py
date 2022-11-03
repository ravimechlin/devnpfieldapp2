def lock(self):
    memcache.set(key="lock_for_" + self._path, value="1", time=60)
