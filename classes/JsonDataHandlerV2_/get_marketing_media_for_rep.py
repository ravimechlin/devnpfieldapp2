def get_marketing_media_for_rep(self):
    self.response.content_type = "application/json"
    ret_json = {}
    ret_json["video"] = Helpers.gcs_file_exists("/MarketingCollateral/" + self.request.get("marketing_key") + "/" + self.request.get("identifier") + "/video.mp4")
    ret_json["image"] = Helpers.gcs_file_exists("/MarketingCollateral/" + self.request.get("marketing_key") + "/" + self.request.get("identifier") + "/image.jpg")
    self.response.out.write(json.dumps(ret_json))
