@staticmethod
def pacific_now():
    now = datetime.now()
    today = now.date()
    keyy = "utc_pacific_offset_" + str(today.month) + "_" + str(today.day) + "_" + str(today.year)

    val = memcache.get(keyy)

    hours_behind = 0

    if val is None:

        time_zone_api_success = False
        #ask for DST status from timezonedb.com
        urll = "https://api.timezonedb.com/?zone=America/Los_Angeles&key=ZJK8HOHCPJV1&format=json"

        try:
            result = urlfetch.fetch(url=urll,
                                    deadline=30)

            if result.status_code == 200:
                #check that it's actually JSON
                header_val = str(result.header_msg.getheaders("Content-Type")[0])

                if not header_val == "":

                    if header_val.lower() == "application/json":

                        json_data = json.loads(result.content)

                        if str(json_data["status"]) == "OK":

                            if str(json_data["dst"]) == "1" or str(json_data["dst"]).lower() == "true":
                                hours_behind = 7
                            else:
                                hours_behind = 8

                            time_zone_api_success = True

            else:
                time_zone_api_success = False

        except:
            time_zone_api_success = False

        google_maps_api_success = False
        if not time_zone_api_success:
            logging.info("heretimezone")
            #try for the google maps timezone api
            result2 = urlfetch.fetch("https://maps.googleapis.com/maps/api/timezone/json?location=34.0801026,-117.75010780000001&timestamp=" + str(time.time()))

            if result2.status_code == 200:
                logging.info("here3googlemaps")
                #check that it's actually JSON

                try:
                    json_data2 = json.loads(result2.content)

                    if int(json_data2["dstOffset"]) > 0:
                        hours_behind = 8 - int(int(json_data2["dstOffset"]) / 60 / 60)
                    else:
                        hours_behind = 7

                    google_maps_api_success = True

                except:
                    logging.info("here7")
                    google_maps_api_success = False
            else:
                logging.info("here8")
                google_maps_api_success = False

        if (not time_zone_api_success) and (not google_maps_api_success):

            #assume march and november are the daylight savings hours
            hours_behind = 8

            if today.month > 3 and today.month < 11:
                hours_behind = 7

        memcache.set(key=keyy, value=str(hours_behind), time=60 * 60 * 24 * 2)

    else:
        hours_behind = int(val)

    return now + timedelta(hours=hours_behind * -1)

