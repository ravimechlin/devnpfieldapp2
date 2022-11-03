@staticmethod
def get_box_auth(server,state,code):

    from boxsdk import OAuth2
    box_settings = Helpers.get_box_settings()

    client_id = box_settings["CLIENT_ID"]
    client_secret = box_settings["CLIENT_SECRET"]

    if (state is None) or (code is None):
        oauth = OAuth2(
            client_id=client_id,
            client_secret=client_secret,
        )
        auth_url, csrf_token = oauth.get_authorization_url("https://" + server + "/data?fn=box_oauth")

        return auth_url, csrf_token

    else:
        csrf_token = memcache.get("box_csrf_token")
        assert state == csrf_token
        oauth = OAuth2(
                client_id=client_id,
                client_secret=client_secret,
            )
        access_token, refresh_token = oauth.authenticate(code)

        access_token_old = None
        refresh_token_old = None

        box_access_token_kv = KeyValueStoreItem.query(KeyValueStoreItem.keyy == "box_access_token")

        for item in box_access_token_kv:
            access_token_old = item.val

        box_refresh_token_kv = KeyValueStoreItem.query(KeyValueStoreItem.keyy == "box_refresh_token")

        for item in box_refresh_token_kv:
            refresh_token_old = item.val

        if access_token_old is None or refresh_token_old is None:


            kv_item_1 = KeyValueStoreItem(
                identifier = Helpers.guid(),
                keyy = "box_access_token",
                val = access_token,
                expiration=datetime(1970, 1, 1)
            )

            kv_item_1.put()

            kv_item_2 = KeyValueStoreItem(
                identifier = Helpers.guid(),
                keyy = "box_refresh_token",
                val = refresh_token,
                expiration=datetime(1970, 1, 1)
            )

            kv_item_2.put()

        else:
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

        return oauth
