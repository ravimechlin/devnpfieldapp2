def post(self):
    import json
    import base64
    from datetime import date
    import hashlib

    post_body = str(self.request.body)
    parsed_info = json.loads(post_body)

    json_whitepages = {}
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "white_pages_info_" + hashlib.md5(str(parsed_info["url"])).hexdigest())
    if kv is None:
        url = parsed_info["url"]

        response = urlfetch.fetch(
                    url=url,
                    method=urlfetch.POST,
                    deadline=30,
                    follow_redirects=True
                )
        json_whitepages = json.loads(response.content)
        logging.info(url)
        logging.info(json_whitepages)
        kv2 = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="white_pages_info_" +  hashlib.md5(str(parsed_info["url"])).hexdigest(),
            val=response.content,
            expiration=Helpers.pacific_now() + timedelta(days=180)
        )
        kv2.put()
        wp = WhitePagesData.first(WhitePagesData.url == parsed_info["url"])
        if not wp is None:
            wp.key.delete()

        o_f = "None"
        o_l = "None"
        a_r = "Unknown"
        try:
            o_f = json_whitepages["owners"][0]["firstname"]
            o_l = json_whitepages["owners"][0]["lastname"]
            a_r = json_whitepages["owners"][0]["age_range"]
        except:
            o_f = o_f

        if o_f is None:
            o_f = "None"
        if o_l is None:
            o_l = "None"
        if a_r is None:
            a_r = "Unknown"

        if json_whitepages["lat_long"]["latitude"] == None or json_whitepages["lat_long"]["longitude"] == None:
            json_whitepages["lat_long"]["latitude"] = -500
            json_whitepages["lat_long"]["longitude"] = -500
            
        wp = WhitePagesData(
            identifier=Helpers.guid(),
            is_valid=str(json_whitepages["is_valid"]),
            street_line_1=str(json_whitepages["street_line_1"]),
            street_line_2=str(json_whitepages["street_line_2"]),
            city=str(json_whitepages["city"]),
            postal_code=str(json_whitepages["postal_code"]),
            zip4=str(json_whitepages["zip4"]),
            state_code=str(json_whitepages["state_code"]),
            country_code=str(json_whitepages["country_code"]),
            longitude=float(json_whitepages["lat_long"]["latitude"]),
            latitude=float(json_whitepages["lat_long"]["longitude"]),
            is_active=str(json_whitepages["is_active"]),
            last_sale_date=str(json_whitepages["last_sale_date"]),
            total_value=str(json_whitepages["total_value"]),
            owner_first=o_f,
            owner_last=o_l,
            age_range=a_r,
            url=parsed_info["url"]
        )
        wp.put()
    else:
        #Helpers.send_email("rnirnber@gmail.com", "Cache Hit", "Cache Hit")
        json_whitepages = json.loads(kv.val)

    o_f = "None"
    o_l = "None"
    a_r = "Unknown"
    try:
        o_f = str(json_whitepages["owners"][0]["firstname"])
        o_l = str(json_whitepages["owners"][0]["lastname"])
        a_r = str(json_whitepages["owners"][0]["age_range"])
    except:
        o_f = o_f
    
    user_fields = {
        "id":json_whitepages["id"],
        "is_valid":str(json_whitepages["is_valid"]),
        "street_line_1":json_whitepages["street_line_1"],
        "street_line_2":json_whitepages["street_line_2"],
        "city":json_whitepages["city"],
        "postal_code":json_whitepages["postal_code"],
        "zip4":json_whitepages["zip4"],
        "state_code":json_whitepages["state_code"],
        "country_code":json_whitepages["country_code"],
        "lat": str(json_whitepages["lat_long"]["latitude"]),
        "lng": str(json_whitepages["lat_long"]["longitude"]),
        "is_active":str(json_whitepages["is_active"]),
        "delivery_point":json_whitepages["delivery_point"],
        "last_sale_date":json_whitepages["last_sale_date"],
        "total_value":str(json_whitepages["total_value"]),
        "owner_first": o_f,
        "owner_last": o_l,
        "age_range" : a_r,
        "current_residents": json_whitepages["current_residents"],
        "owners": json_whitepages["owners"]
    }

    self.response.out.write(json.dumps(user_fields))
