def marketing_resize_video(self):
    from datetime import datetime
    from datetime import timedelta
    from google.appengine.api import urlfetch
    from StringIO import StringIO
    from io import BytesIO
    import time
    import cloudstorage as gcs
    from google.appengine.api import app_identity

    time.sleep(10)
    start_dt = datetime.now()
        
    aspect = self.request.get("aspect")
    video_url = self.request.get("url")
    token = self.request.get("token")
    rep_identifier = self.request.get("rep_identifier")
    marketing_key = self.request.get("marketing_key")

    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "video_processing_" + token)

    req_headers = {}
    req_headers["Accept"] = "application/json"
    req_headers["Content-Type"] = "application/json"
    req_headers["Zencoder-Api-Key"] = "0ac631c2ada5363d2471d3fde74ce52d"                                 

    post_payload = {"input": video_url}
    post_payload["api_key"] = "0ac631c2ada5363d2471d3fde74ce52d"
    post_payload["size"] = "320x240"
    if aspect == "portrait":
        post_payload["size"] = "240x320"
    post_payload["skip"] = {"max_duration": 30}
    post_payload["outputs"] = [{}]
    post_payload["outputs"][0]["size"] = post_payload["size"]
    post_payload["outputs"][0]["audio_bitrate"] = 10
    post_payload["outputs"][0]["max_video_bitrate"] = 200
    post_payload["outputs"][0]["h264_profile"] = "baseline"
    post_payload["outputs"][0]["h264_level"] = "3.1"
    post_payload["outputs"][0]["max_frame_rate"] = 30
    post_payload["outputs"][0]["format"] = "mp4"

    req = urlfetch.fetch("https://app.zencoder.com/api/v2/jobs.json",
                        method=urlfetch.POST,
                        deadline=30,
                        payload=json.dumps(post_payload))

    ret = False    
    resp = {}
    try:
        resp = json.loads(req.content)
        x = resp["outputs"][0]["url"]
    except:
        kv.val = "An error has occured"
        kv.put()
        ret = True

    if ret:
        return

    x = 5
    total_seconds = (datetime.now() - start_dt).total_seconds()
    success = False
    Helpers.send_email("rnirnber@gmail.com", "content", req.content)
    while total_seconds < 300 and (not success):
        req2 = urlfetch.fetch(resp["outputs"][0]["url"],
                                method=urlfetch.GET,
                                deadline=60)
        if req2.status_code == 200 and req2.header_msg.getheaders("Content-Type")[0] == "video/3gp":
            success = True
            content = StringIO(req2.content)
            content.seek(0)
            f = GCSLockedFile("/TempVideos/" + token + ".3gp")
            #f = GCSLockedFile("/testing.txt")
            f.unlock()                
            f.write(content.getvalue(), "video/mp4", "public-read")
            #f.write("testing", "text/plain", "public-read")
            content.close()
            time.sleep(5)
            filesize = Helpers.gcs_file_size("/TempVideos/" + token + ".3gp")
            filesize /= 1024
            filesize /= 1024
            if filesize > 0.45:
                kv.val = "The filesize was too large. (" + str(filesize) + " MB). Please try clipping the video to a shorter length or compressing it."
                kv.put()
            else:
                if not rep_identifier == "-1":
                    Helpers.gcs_copy("/TempVideos/" + token + ".3gp", "/MarketingCollateral/" + marketing_key + "/" + rep_identifier + "/video.3gp", "video/3gp", "public-read")
                    time.sleep(2)
                else:
                    Helpers.gcs_copy("/TempVideos/" + token + ".3gp", "/MarketingCollateral/" + marketing_key + "/fallback.3gp", "video/3gp", "public-read")
                time.sleep(5)
                bucket_name = os.environ.get('BUCKET_NAME',
                                 app_identity.get_default_gcs_bucket_name())

                bucket = '/' + bucket_name
                filename = bucket + "/TempVideos/" + token + ".3gp"

                retryParameters = gcs.RetryParams(initial_delay=0.2,
                                                max_delay=5.0,
                                                backoff_factor=2,
                                                max_retry_period=15,
                                                urlfetch_timeout=30)

                gcs.delete(filename)
                filename2 = bucket + "/temp_videos/" + token + ".mp4"
                gcs.delete(filename2)

                kv.val = "The video has been uploaded"
                kv.put()
            
        time.sleep(10)
        total_seconds = (datetime.now() - start_dt).total_seconds()
    
    if not success:
        kv.val = "The video you uploaded is taking to long to process, please cancel and try again"
        kv.put()
