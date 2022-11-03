def post(self, keyyy):
    """
        Adds a new k-v pair to the KeyValueStoreItem table.
        
        Accepts a single key value pair or a `|||` separated ordered list
        of values.
        
        An optional time-to-live value `ttl` can be set per request. Setting
        a negative TTL will cause the k-v pair to have an expiration date
        at the unix epoch.
    """
    
    # TODO should the mime type be set elsewhere?
    self.response.content_type = "application/json"
    
    
    value = str(self.request.get("value"))

    ttl = str(self.request.get("ttl")).lower()
    if (not ttl == "") and not (ttl == "none"):
        try:
            ttl = int(ttl)
        except ValueError:
            ttl = -1
    else:
        ttl = -1
    
    
    # allow a save forever request with a negative TTL
    if ttl < 0:
        # unix epoch time
        expiration = datetime.fromtimestamp(0)
    else:
        expiration = Helpers.pacific_now() + timedelta(seconds=ttl)
    
    if not value == "" and not value.lower() == "none":
        
        # overwrites uniques
        existing_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy == keyyy)
        for existing_item in existing_items:
            existing_item.key.delete()
        
        guid = Helpers.guid()
        key_value_store_item = KeyValueStoreItem(
            identifier=guid,
            keyy=keyyy,
            val=value,
            expiration=expiration
        )
        
        key_value_store_item.put()
        stored = {}
        stored['identifier'] = guid
        stored['keyy'] = keyyy
        stored['val'] = value
        stored['ttl'] = ttl
        stored['expiration'] = expiration.strftime("%Y-%m-%d %H:%M:%S")
        
        ret_json = stored
        self.response.out.write(json.dumps(ret_json))
        
        
    
    ### A Multi request
    
    values = str(self.request.get("values"))

    if not values == "" and not values.lower() == "none":
        keyyys = keyyy.split("|||")
        vals = values.split("|||")

        existing_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(keyyys))

        for existing_item in existing_items:
            existing_item.key.delete()

        count = 0
        items_to_add = []
        totalstored = []
        while count < len(keyyys):
            guid = Helpers.guid()
            key_value_store_item = KeyValueStoreItem(
                identifier=guid,
                keyy=keyyys[count],
                val=vals[count],
                expiration=expiration
            )
            stored = {}
            stored['identifier'] = guid
            stored['keyy'] = keyyys[count]
            stored['val'] = vals[count]
            stored['ttl'] = ttl
            stored['expiration'] = expiration.strftime("%Y-%m-%d %H:%M:%S")
            totalstored.append(stored)
            items_to_add.append(key_value_store_item)
            count +=1

        ndb.put_multi(items_to_add)
        
        ret_json = {}
        ret_json["result"] = totalstored
        self.response.out.write(json.dumps(ret_json))


