@staticmethod
def get_pricing_structures():
    content = "{}"
    cached_content = memcache.get("pricing_structures")
    if not cached_content is None:
        content = cached_content
    else:
        f = GCSLockedFile("/ApplicationSettings/pricing_structures_" + app_identity.get_application_id() + ".json")
        c = f.read()
        if not c is None:
            content = c
            memcache.set(key="pricing_structures", value=content, time=3600)
    return json.loads(content)

