@staticmethod
def grant_box_collaboration(email,user_type):

    from boxsdk import OAuth2
    from boxsdk import Client

    access_token = memcache.get("box_access_token")
    refresh_token = memcache.get("box_refresh_token")

    if access_token is None or refresh_token is None:

        box_access_token_kv = KeyValueStoreItem.query(KeyValueStoreItem.keyy == "box_access_token")

        for item in box_access_token_kv:
            access_token = item.val

        box_refresh_token_kv = KeyValueStoreItem.query(KeyValueStoreItem.keyy == "box_refresh_token")

        for item in box_refresh_token_kv:
            refresh_token = item.val

    box_settings = Helpers.get_box_settings()

    client_id = box_settings["CLIENT_ID"]
    client_secret = box_settings["CLIENT_SECRET"]

    if user_type == "survey":
        folder_id = box_settings["SURVEYOR_FOLDER_ID"]
        role = box_settings["SURVEYOR_PERM"]
    else:
        folder_id = box_settings["REP_MGR_FOLDER_ID"]
        role = box_settings["REP_MGR_PERM"]

    oauth = OAuth2(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    client = Client(oauth)
    root_folder = client.folder(folder_id=folder_id)
    resp = None
    collaboration = root_folder.add_collaborator(email, role, resp, True)
    resp = collaboration.get_resp_dct()

    if "status" in resp.keys():
        return resp["status"].lower() == "pending"
    return False
