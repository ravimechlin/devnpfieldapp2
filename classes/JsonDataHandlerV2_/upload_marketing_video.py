def upload_marketing_video(self):
    import time
    from google.appengine.api import taskqueue
    from google.appengine.api import app_identity
    from datetime import datetime
    from datetime import timedelta

    self.response.content_type = "application/json"
    ret_json = {"token": Helpers.guid()}
    
    parameters = {}
    parameters["url"] = "https://storage.googleapis.com/" + app_identity.get_default_gcs_bucket_name() + "/temp_videos/" + ret_json["token"] + ".mp4"
    parameters["aspect"] = self.request.get("aspect")
    parameters["token"] = ret_json["token"]
    parameters["rep_identifier"] = self.request.get("rep_identifier")
    parameters["marketing_key"] = self.request.get("marketing_key")

    kv = KeyValueStoreItem(
        identifier=Helpers.guid(),
        keyy="video_processing_" + parameters["token"],
        val="Processing video...",
        expiration=Helpers.pacific_now() + timedelta(minutes=30)
    )
    kv.put()
    taskqueue.add(url="/tq/marketing_resize_video", params=parameters, eta=datetime.now() + timedelta(seconds=5))
    
    file_content = self.request.POST.multi['video'].file.read()
    f = GCSLockedFile("/temp_videos/" + ret_json["token"] + ".mp4")
    f.write(file_content, "video/mp4", "public-read")
    f.unlock()

    self.response.out.write(json.dumps(ret_json))
