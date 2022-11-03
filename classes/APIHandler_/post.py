def post(self, method):
    from PIL import Image
    from io import BytesIO
    from google.appengine.api import urlfetch
    import StringIO
    self.session = get_current_session()
    if method[-1] == "/":
        method = method[0:len(method) - 1]

    self.response.content_type = "application/json"
    ret_json = {}
    if method == "geolocation/postal_details":
        req = urlfetch.fetch(
                url="https://maps.googleapis.com/maps/api/geocode/json?address=" + self.request.get("postal"),
                method=urlfetch.GET,
                deadline=30
        )
        jaysawn = {}
        try:
            jaysawn = json.loads(req.content)
            ret_json["city"] = "n/a"
            ret_json["state"] = ""
            ret_json["county"] = "n/a"

            if "results" in jaysawn.keys():
                if len(jaysawn["results"]) > 0:
                    result = jaysawn["results"][0]
                    if "address_components" in result.keys():
                        if len(result["address_components"]) > 1:
                            component = result["address_components"][1]
                            if "long_name" in component.keys():
                                ret_json["city"] = component["long_name"]

                        cnt = 0
                        while(cnt < len(result["address_components"])):
                            component = result["address_components"][cnt]
                            if "types" in component.keys():
                                if len(component["types"]) > 0:
                                    typee = component["types"][0]
                                    if typee == "administrative_area_level_1":
                                        if "short_name" in component.keys():
                                            ret_json["state"] = component["short_name"]

                                    elif typee == "administrative_area_level_2":
                                        if "long_name" in component.keys():
                                            ret_json["county"] = component["long_name"]

                            cnt += 1

            if ret_json["city"] == "n/a" or ret_json["state"] == "" or ret_json["county"] == "n/a":
                self.fail_request()
        except:
            self.fail_request()


    if method == "lead_id":
        import hashids
        from random import randint
        r_int = randint(1,1000)
        hids = hashids.Hashids("abc902ielKKLLMM22", 8, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890");
        lead_id = hids.encode(int((datetime.now() - datetime(1970, 1, 1)).total_seconds()), r_int);
        ret_json["lead_id"] = lead_id

    if method == "sales_form_info":
        import hashids
        from random import randint
        r_int = randint(1,1000)
        hids = hashids.Hashids("abc902ielKKLLMM22", 8, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890");
        lead_id = hids.encode(int((datetime.now() - datetime(1970, 1, 1)).total_seconds()), r_int)
        ret_json["lead_id"] = lead_id

        ret_json["utility_providers"] = Helpers.list_utility_providers()
        ret_json["rep_id"] = self.session["user_rep_id"]
        ret_json["phone"] = Helpers.format_phone_number(self.session["user_phone"])
        ret_json["email"] = self.session["user_email"]
        ret_json["offices"] = []
        ret_json["user_office"] = self.session["user_rep_office"]

        offices = []
        office_locations = OfficeLocation.query(OfficeLocation.parent_identifier != "n/a")
        for office_location in office_locations:
            office = {}
            office["identifier"] = office_location.identifier
            office["name"] = office_location.name
            ret_json["offices"].append(office)

    if method == "LB":
        ret_json["data"] = {}
        ret_json["rep_id_to_identifier"] = {}
        ret_json["identifier_to_rep_id"] = {}
        ret_json["rep_id_to_name"] = {}
        users = FieldApplicationUser.query(FieldApplicationUser.current_status == 0)
        for user in users:
            ret_json["rep_id_to_identifier"][user.rep_id] = user.identifier
            ret_json["identifier_to_rep_id"][user.identifier] = user.rep_id
            ret_json["rep_id_to_name"][
                user.rep_id] = user.first_name.strip().title() + " " + user.last_name.strip().title()

        start_dt = datetime.now()
        end_dt = datetime.now()

        lb_stats = []
        lb_stats2 = []
        h_p_t = Helpers.pacific_today()
        if self.request.get("time_metric") == "all_time":
            lb_stats = LeaderBoardStat.query(LeaderBoardStat.metric_key == self.request.get("achievement_metric"))
            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    LeaderBoardStat.metric_key == self.request.get("appointment_cancelled"))

        elif self.request.get("time_metric") == "daily":
            start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
            end_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day, 23, 59, 59)
            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )
            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "weekly":
            start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
            while not start_dt.isoweekday() == 7:
                start_dt = start_dt + timedelta(days=-1)

            start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
            end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
            end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )

            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "monthly":
            start_dt = datetime(h_p_t.year, h_p_t.month, 1)
            end_dt = datetime(h_p_t.year, h_p_t.month, 28)
            while end_dt.month == start_dt.month:
                end_dt = end_dt + timedelta(days=1)

            end_dt = end_dt + timedelta(seconds=-1)

            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )

            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "quarterly":
            months_start_map = {"1": 1, "2": 1, "3": 1, "4": 4, "5": 4, "6": 4, "7": 7, "8": 7, "9": 7, "10": 10,
                                "11": 10, "12": 10}
            months_end_map = {"1": 3, "2": 3, "3": 3, "4": 6, "5": 6, "6": 6, "7": 9, "8": 9, "9": 9, "10": 12,
                              "11": 12, "12": 12}
            days_end_map = {"3": 31, "6": 30, "9": 30, "12": 31}

            start_dt = datetime(h_p_t.year, months_start_map[str(h_p_t.month)], 1)
            end_month = months_end_map[str(h_p_t.month)]
            end_day = days_end_map[str(end_month)]
            end_dt = datetime(h_p_t.year, end_month, end_day, 23, 59, 59)

            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )

            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "yearly":
            start_dt = datetime(h_p_t.year, 1, 1)
            end_dt = datetime(h_p_t.year, 12, 31, 23, 59, 59)

            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )

            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "yesterday":
            start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day) + timedelta(days=-1)
            end_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day) + timedelta(seconds=-1)

            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )

            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "last_week":
            start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
            while not start_dt.isoweekday() == 7:
                start_dt = start_dt + timedelta(days=-1)

            start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
            end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
            end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

            start_dt = start_dt + timedelta(days=-7)
            end_dt = end_dt + timedelta(days=-7)

            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )

            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "last_month":
            start_dt = datetime(h_p_t.year, h_p_t.month, 1)
            start_dt = start_dt + timedelta(days=-1)
            while not start_dt.day == 1:
                start_dt = start_dt + timedelta(days=-1)

            end_dt = datetime(start_dt.year, start_dt.month, start_dt.day, 23, 59, 59)
            curr_month = end_dt.month
            while end_dt.month == curr_month:
                end_dt = end_dt + timedelta(days=1)
            end_dt = end_dt + timedelta(days=-1)

            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )

            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "last_quarter":
            months_start_map = {"1": 10, "2": 10, "3": 10, "4": 1, "5": 1, "6": 1, "7": 4, "8": 4, "9": 4, "10": 7,
                                "11": 7, "12": 7}
            months_end_map = {"1": 12, "2": 12, "3": 12, "4": 3, "5": 3, "6": 3, "7": 6, "8": 6, "9": 6, "10": 9,
                              "11": 9, "12": 9}
            days_end_map = {"3": 31, "6": 30, "9": 30, "12": 31}

            start_dt = datetime(h_p_t.year, months_start_map[str(h_p_t.month)], 1)
            end_month = months_end_map[str(h_p_t.month)]
            end_day = days_end_map[str(end_month)]
            end_dt = datetime(h_p_t.year, end_month, end_day, 23, 59, 59)

            if h_p_t.month < 4:
                start_dt = datetime(start_dt.year - 1, start_dt.month, start_dt.day)
                end_dt = datetime(end_dt.year - 1, end_dt.month, end_dt.day, end_dt.hour, end_dt.minute, end_dt.second)

            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )

            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "last_year":
            start_dt = datetime(h_p_t.year - 1, 1, 1)
            end_dt = datetime(h_p_t.year - 1, 12, 31, 23, 59, 59)

            lb_stats = LeaderBoardStat.query(
                ndb.OR
                    (
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "pacific_time",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt
                    ),
                    ndb.AND
                        (
                        LeaderBoardStat.metric_key == self.request.get("achievement_metric"),
                        LeaderBoardStat.timezone == "mountain_time",
                        LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                        LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                    )
                )
            )

            if self.request.get("achievement_metric") == "leads_acquired":
                lb_stats2 = LeaderBoardStat.query(
                    ndb.OR
                        (
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "pacific_time",
                            LeaderBoardStat.dt >= start_dt,
                            LeaderBoardStat.dt <= end_dt
                        ),
                        ndb.AND
                            (
                            LeaderBoardStat.metric_key == "appointment_cancelled",
                            LeaderBoardStat.timezone == "mountain_time",
                            LeaderBoardStat.dt >= start_dt + timedelta(hours=1),
                            LeaderBoardStat.dt <= end_dt + timedelta(hours=1)
                        )
                    )
                )

        elif self.request.get("time_metric") == "all_time":
            lb_stats = LeaderBoardStat.query(LeaderBoardStat.metric_key == self.request.get("achievement_metric"))
            lb_stats2 = LeaderBoardStat.query(LeaderBoardStat.metric_key == "appointment_cancelled")

        for lb_stat in lb_stats:
            if not lb_stat.rep_id in ret_json["data"].keys():
                ret_json["data"][lb_stat.rep_id] = 0

            ret_json["data"][lb_stat.rep_id] += 1

        for lb_stat in lb_stats2:
            if lb_stat.rep_id in ret_json["data"].keys():
                ret_json["data"][lb_stat.rep_id] -= 1

        ret_json["start_dt"] = str(start_dt.date())
        ret_json["end_dt"] = str(end_dt.date())

    elif method == "user_photo":
        identifier = self.request.get("identifier")
        width = int(self.request.get("width"))
        height = int(self.request.get("height"))
        gcs_file = GCSLockedFile("/Images/ProfilePictures/Full/" + identifier + ".jpg")
        img_data = gcs_file.read()
        if not img_data is None:
            bytez = BytesIO(img_data)
            buff = StringIO.StringIO()
            img = Image.open(bytez)
            img = img.resize((width, height), Image.ANTIALIAS)
            img.save(buff, format="JPEG")
            ret_json["b64"] = base64.b64encode(buff.getvalue())

            bytez.close()
            buff.close()

    elif method == "user_details":
        usr = FieldApplicationUser.first(FieldApplicationUser.identifier == self.session["user_identifier"])
        if not usr is None:
            for item in ["identifier", "rep_phone", "rep_email", "first_name", "last_name", "main_office", "user_type"]:
                ret_json[item] = getattr(usr, item)

            if 5 == 5:
                ret_json["city"] = self.request.headers["X-AppEngine-City"]
                ret_json["state"] = self.request.headers["X-AppEngine-Region"]
                ret_json["temperature"] = ""
                hashed = hashlib.md5((ret_json["city"] + "___" + ret_json["state"]).lower()).hexdigest()
                val = memcache.get(hashed)
                if val is None:
                    req = urlfetch.fetch(
                            url="https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22" + self.request.headers["X-AppEngine-City"].replace(" ", "%20") + "%2C%20" + self.request.headers["X-AppEngine-Region"].replace(" ", "%20") + "%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys",
                            method=urlfetch.GET,
                            deadline=30
                    )
                    data = json.loads(req.content)
                    ret_json["temperature"] = data["query"]["results"]["channel"]["item"]["condition"]["temp"]
                    memcache.set(key=hashed, value=ret_json["temperature"], time=60 * 10)
                else:
                    ret_json["temperature"] = val

                ret_json["abs_today"] = []
                ret_json["abs_this_week"] = []
                ret_json["cds_today"] = []
                ret_json["cds_this_week"] = []

                val2 = memcache.get("leaderboard_homescene_data")
                if val2 is None:
                    pload = {"achievement_metric": "leads_acquired", "time_metric": "daily"}
                    req2 = urlfetch.fetch(
                        url="https://" + app_identity.get_application_id() + ".appspot.com/API/LB/",
                        method=urlfetch.POST,
                        payload=urllib.urlencode(pload),
                        deadline=30
                    )
                    jaysawn = json.loads(req2.content)
                    if "data" in jaysawn.keys():
                        if len(jaysawn["data"].keys()) > 0:
                            r_ids = jaysawn["data"].keys()
                            for r_id in r_ids:
                                if jaysawn["data"][r_id] > 0:
                                    if r_id in jaysawn["rep_id_to_name"].keys():
                                        ret_json["abs_today"].append({"name": jaysawn["rep_id_to_name"][r_id], "tally": jaysawn["data"][r_id]})

                    pload2 = {"achievement_metric": "leads_acquired", "time_metric": "weekly"}
                    req3 = urlfetch.fetch(
                        url="https://" + app_identity.get_application_id() + ".appspot.com/API/LB/",
                        method=urlfetch.POST,
                        payload=urllib.urlencode(pload2),
                        deadline=30
                    )
                    jaysawn = json.loads(req3.content)
                    if "data" in jaysawn.keys():
                        if len(jaysawn["data"].keys()) > 0:
                            r_ids = jaysawn["data"].keys()
                            for r_id in r_ids:
                                if jaysawn["data"][r_id] > 0:
                                    if r_id in jaysawn["rep_id_to_name"].keys():
                                        ret_json["abs_this_week"].append({"name": jaysawn["rep_id_to_name"][r_id], "tally": jaysawn["data"][r_id]})


                    pload3 = {"achievement_metric": "packets_submitted", "time_metric": "daily"}
                    req4 = urlfetch.fetch(
                        url="https://" + app_identity.get_application_id() + ".appspot.com/API/LB/",
                        method=urlfetch.POST,
                        payload=urllib.urlencode(pload3),
                        deadline=30
                    )

                    jaysawn = json.loads(req4.content)
                    if "data" in jaysawn.keys():
                        if len(jaysawn["data"].keys()) > 0:
                            r_ids = jaysawn["data"].keys()
                            for r_id in r_ids:
                                if jaysawn["data"][r_id] > 0:
                                    if r_id in jaysawn["rep_id_to_name"].keys():
                                        ret_json["cds_today"].append({"name": jaysawn["rep_id_to_name"][r_id], "tally": jaysawn["data"][r_id]})

                    pload4 = {"achievement_metric": "packets_submitted", "time_metric": "weekly"}
                    req5 = urlfetch.fetch(
                        url="https://" + app_identity.get_application_id() + ".appspot.com/API/LB/",
                        method=urlfetch.POST,
                        payload=urllib.urlencode(pload4),
                        deadline=30
                    )

                    jaysawn = json.loads(req5.content)
                    if "data" in jaysawn.keys():
                        if len(jaysawn["data"].keys()) > 0:
                            r_ids = jaysawn["data"].keys()
                            for r_id in r_ids:
                                if jaysawn["data"][r_id] > 0:
                                    if r_id in jaysawn["rep_id_to_name"].keys():
                                        ret_json["cds_this_week"].append({"name": jaysawn["rep_id_to_name"][r_id], "tally": jaysawn["data"][r_id]})

                        #memcache.set(key="leaderboard_homescene_data", value=json.dumps(ret_json["lb_data_items"]), time=600)
                else:
                    ret_json["lb_data_items"] = json.loads(val2)

            else:
                usr = usr
        else:
            self.fail_request()

    self.session.terminate()
    self.response.out.write(json.dumps(ret_json))
