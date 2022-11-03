def upload_marketing_image(self):
    file_content = self.request.POST.multi['image'].file.read()
    marketing_key = self.request.get("marketing_key")
    rep_identifier = self.request.get("rep_identifier")
    path = "/MarketingCollateral/" + marketing_key + "/"
    if rep_identifier == "-1":
        path += "fallback.jpg"
    else:
        path += rep_identifier + "/" + "image.jpg"
    
    f = GCSLockedFile(path)
    f.write(file_content, "image/jpeg", "public-read")
    f.unlock()
