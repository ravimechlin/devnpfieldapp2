@staticmethod
def create_file_in_google_drive(parent_folder_id, nayme, b64_str, mime_type):
    import StringIO
    import json
    import base64

    import StringIO
    import httplib2
    from oauth2client.service_account import ServiceAccountCredentials
    from apiclient.discovery import build
    from apiclient.http import MediaIoBaseUpload

    from oauth2client import client



    from oauth2client.client import OAuth2WebServerFlow
    from oauth2client.client import OAuth2Credentials
    from oauth2client import GOOGLE_AUTH_URI
    from oauth2client import GOOGLE_REVOKE_URI
    from oauth2client import GOOGLE_TOKEN_URI

    REFRESH_TOKEN = "1/8Vb04HoTM7ootTe3G-tcJ_TKuXo31HGOG6r4ui343_0"
    CLIENT_ID = "7243489703-7h4g1esc4i2oqcgngbb8gvnqdlcorl6u.apps.googleusercontent.com"
    CLIENT_SECRET = '83QmOX_Pl6EAlDVJz8z9ws0-'

    OAUTH_SCOPE = ['https://www.googleapis.com/auth/drive']

    REDIRECT_URI = 'https://' + app_identity.get_application_id() + '/data?fn=drive_oauth'

    credentials = OAuth2Credentials(None, CLIENT_ID,
                           CLIENT_SECRET, REFRESH_TOKEN, None,
                           GOOGLE_TOKEN_URI, None,
                           revoke_uri=GOOGLE_REVOKE_URI,
                           id_token=None,
                           token_response=None)
    http = httplib2.Http()
    http_auth = credentials.authorize(http)
    drive = build('drive', 'v2', http=http_auth)



    io_buff = StringIO.StringIO(base64.b64decode(b64_str))
    mediabody = MediaIoBaseUpload(io_buff, mimetype="image/jpeg")
    body = {
        'title': nayme,
        'mimeType': mime_type,
        'parents': [{'id': parent_folder_id}],
    }
    f = drive.files().insert(
        body=body,
        media_body=mediabody
    ).execute()
    io_buff.close()
    return f["id"]




