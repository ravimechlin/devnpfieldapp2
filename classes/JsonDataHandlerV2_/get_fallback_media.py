def get_fallback_media(self):
    self.response.content_type = "application/json"
    ret_json = {"data": []}
    intro_video_exists = Helpers.gcs_file_exists("/MarketingCollateral/introductory_selfie/fallback.mp4")
    intro_image_exists = Helpers.gcs_file_exists("/MarketingCollateral/introductory_selfie/fallback.jpg") 
    ret_json["data"].append({"key": "introductory_selfie", "name": "Introductory Selfie", "video": intro_video_exists, "image": intro_image_exists})

    self.response.out.write(json.dumps(ret_json))
