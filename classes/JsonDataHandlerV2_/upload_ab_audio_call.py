def upload_ab_audio_call(self):
    from google.appengine.api import urlfetch
    import time
    import base64

    identifier = self.request.get("identifier")
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == identifier)
    if not app_entry is None:
        f = GCSLockedFile("/AudioRecordings/ABs/" + identifier + ".mp3")
        f.write(base64.b64decode(self.request.get("b64")), "audio/mpeg", "public-read")
        f.unlock()

        root_folder = ThirdPartyFolder.first(
            ndb.AND(
                ThirdPartyFolder.field_app_identifier == identifier,
                ThirdPartyFolder.folder_key == "root_folder"
            )
        )
        if not root_folder is None:
            audio_folder = ThirdPartyFolder.first(
                ndb.AND(
                    ThirdPartyFolder.field_app_identifier == identifier,
                    ThirdPartyFolder.folder_key == "audio_recordings"
                )
            )
            parent_id = "-1"
            if audio_folder is None:
                parent_id = Helpers.create_customer_folder_in_google_drive(app_entry, root_folder.foreign_id, "Audio Recordings", "audio_recordings")
            else:
                parent_id = audio_folder.foreign_id

            file_id = Helpers.create_file_in_google_drive(parent_id, "AB.mp3", self.request.get("b64"), "audio/mpeg")

            time.sleep(1)
            resp = urlfetch.fetch(url="https://script.google.com/macros/s/AKfycbx5qjSkvfPesmdL5pOUnofY0dxikB9G0MgqIXdJlZdq6vkv-7zy/exec?id=" + file_id,
                deadline=60,
                method=urlfetch.GET)
            mp3_url = resp.content

            kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "ab_call_recording_" + app_entry.identifier)
            if kv is None:
                kv = KeyValueStoreItem(
                    identifier=Helpers.guid(),
                    keyy="ab_call_recording_" + app_entry.identifier,                    
                    expiration=datetime(1970, 1, 1)
                )
            kv.val = mp3_url
            kv.put()
