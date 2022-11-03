def unlock(self):
    memcache.delete("lock_for_" + self._path)
