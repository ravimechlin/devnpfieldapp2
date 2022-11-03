@staticmethod
def kill_ndb_schema_cache(clsname):
    key1 = "attributes_for_" + clsname
    key2 = "definition_for_" + clsname
    memcache.delete(key1)
    memcache.delete(key2)

