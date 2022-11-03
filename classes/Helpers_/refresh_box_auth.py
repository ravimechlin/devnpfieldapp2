@staticmethod
def refresh_box_auth():

    from boxsdk import OAuth2

    access_token_old = memcache.get("box_access_token")
    refresh_token_old = memcache.get("box_refresh_token")

    if access_token_old is None or refresh_token_old is None:

        box_access_token_kv = KeyValueStoreItem.query(KeyValueStoreItem.keyy == "box_access_token")

        for item in box_access_token_kv:
            access_token_old = item.val

        box_refresh_token_kv = KeyValueStoreItem.query(KeyValueStoreItem.keyy == "box_refresh_token")

        for item in box_refresh_token_kv:
            refresh_token_old = item.val

    box_settings = Helpers.get_box_settings()
    client_id = box_settings["CLIENT_ID"]
    client_secret = box_settings["CLIENT_SECRET"]

    oauth = OAuth2(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token_old,
        refresh_token=refresh_token_old,
        )

    access_token, refresh_token = oauth.refresh(access_token_old)

    if not access_token == access_token_old:

        kv_items_1 = KeyValueStoreItem.query(KeyValueStoreItem.keyy == "box_access_token")

        for item in kv_items_1:
            item.val = access_token
            item.put()

        kv_items_2 = KeyValueStoreItem.query(KeyValueStoreItem.keyy == "box_refresh_token")

        for item in kv_items_2:
            item.val = refresh_token
            item.put()

        memcache.set("box_access_token", access_token, 3600)
        memcache.set("box_refresh_token", refresh_token, 3600)


        return access_token
