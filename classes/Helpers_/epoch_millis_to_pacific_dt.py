@staticmethod
def epoch_millis_to_pacific_dt(millis):
    req_headers_dict = {}
    req_headers_dict["Accept"] = "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01"
    req_headers_dict["Accept-Language"] = "en-US,en;q=0.8"
    req_headers_dict["Connection"] = "keep-alive"
    req_headers_dict["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"

    dt = datetime.utcfromtimestamp(millis / 1000)
    url = "https://maps.googleapis.com/maps/api/timezone/json?location=34.0207488,-118.6926012&timestamp=" + str(millis / 1000) + "&key=AIzaSyC1JStq4qg-S61Y1bAXLzAWlq3ToUIscZk"
    resp = urlfetch.fetch(
        url=url,
        method=urlfetch.GET,
        deadline=30,
        headers=req_headers_dict,
        follow_redirects=True
    )

    response_json = json.loads(resp.content.strip())
    return ((dt + timedelta(seconds=int(response_json["rawOffset"]))) + timedelta(seconds=int(response_json["dstOffset"])))




