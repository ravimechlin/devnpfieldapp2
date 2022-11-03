def post(self):
    import json
    import base64
    import random
    from datetime import date
    from datetime import datetime
    from datetime import timedelta
    from google.appengine.api import taskqueue
    
    
    post_body = unicode(self.request.body.decode("utf-8"))
    logging.info("The post body...")
    logging.info(post_body)
    parsed_info = json.loads(post_body)
    logging.info(parsed_info)
    
    if parsed_info["type"] == "PinPoint":        

        pin_entry = PinPoint(
            identifier=Helpers.guid(),
            quadrant_identifier=Helpers.guid(),
            rep_identifier=parsed_info["rep_identifier"],
            longitude=float(parsed_info["longitude"]),
            latitude=float(parsed_info["latitude"]),
            status=int(parsed_info["status"]),
            extra_info=parsed_info["extra_info"],
            created=Helpers.pacific_now(),
            modified=Helpers.pacific_now(),
            manager_identifier=parsed_info["manager_identifier"],
            )
        pin_entry.put()
        self.response.set_status(200)
        self.response.out.write(pin_entry.identifier)

    elif parsed_info["type"] == "DinnerGoalSave":
        dt = Helpers.pacific_now()
        while not dt.isoweekday() == 7:
            dt = dt + timedelta(days=-1)
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "dinner_goals_" + str(dt.date()).replace("-", "_") + "_" + parsed_info["identifier"])
        if kv is None:
            kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="dinner_goals_" + str(dt.date()).replace("-", "_") + "_" + parsed_info["identifier"],
                val=json.dumps({"AB": int(parsed_info["AB"]), "CD": int(parsed_info["CD"]), "AK": int(parsed_info["AK"])}),
                expiration=datetime(1970, 1, 1)
            )
            kv.put()

    elif parsed_info["type"] == "DinnerGoalsCheck":
        dt = Helpers.pacific_now()
        while not dt.isoweekday() == 7:
            dt = dt + timedelta(days=-1)
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "dinner_goals_" + str(dt.date()).replace("-", "_") + "_" + parsed_info["identifier"])
        ret_json = {"prompt": (kv is None)}

    elif parsed_info["type"] == "DebugFunction1":
        f = GCSLockedFile("/app_debuggings/function_1.json")
        content = f.read()
        if content is None:
            content = "[]"
        content = json.loads(content)
        content.append(parsed_info["message"] + "|" + str(Helpers.pacific_now()))
        f.write(json.dumps(content), "application/json", "public-read")

    elif parsed_info["type"] == "VersionCheck":
        ret_json = {}
        ret_json["version"] = Helpers.get_app_version()

    elif parsed_info["type"] == "ResolveRepNameAndTimestamp":
        ret_json = {"first_name": "", "last_name": "", "timestamp": "1970-01-01 00:00:00"}
        rep = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["identifier"])
        if not rep is None:
            ret_json["first_name"] = rep.first_name.strip().title()
            ret_json["last_name"] = rep.last_name.strip().title()

        quadrant = RepQuadrant.first(RepQuadrant.identifier == parsed_info["quadrant_identifier"])
        if not quadrant is None:
            ret_json["timestamp"] = str(quadrant.modified).split(".")[0]

    elif parsed_info["type"] == "RepQuadrantQuery":
        quadrants = RepQuadrant.query(
            ndb.AND(
                RepQuadrant.rep_identifier == parsed_info["identifier"],
                RepQuadrant.active == True
            )
        )
        ret_json = []
        for quadrant in quadrants:
            obj = {"active": quadrant.active, "identifier": quadrant.identifier, "rep_identifier": quadrant.rep_identifier, "manager_identifier": quadrant.manager_identifier, "all_points": json.loads(quadrant.all_points)}
            ret_json.append(obj)

    elif parsed_info["type"] == "RepQuadrantSingleQuery":
        quadrant = RepQuadrant.first(
                RepQuadrant.identifier == parsed_info["identifier"]
        )
        ret_json = []
        obj = {"active": quadrant.active, "identifier": quadrant.identifier, "rep_identifier": quadrant.rep_identifier, "manager_identifier": quadrant.manager_identifier,"office_identifier": quadrant.office_identifier, "all_points": json.loads(quadrant.all_points)}
        ret_json.append(obj)

    elif parsed_info["type"] == "ManagerQuadrantQuery":
        quadrants = RepQuadrant.query(RepQuadrant.office_identifier == parsed_info["office_identifier"])
        ret_json = []
        for quadrant in quadrants:
            obj = {"active": quadrant.active, "identifier": quadrant.identifier, "rep_identifier": quadrant.rep_identifier, "manager_identifier": quadrant.manager_identifier, "office_identifier": quadrant.office_identifier, "all_points": json.loads(quadrant.all_points)}
            ret_json.append(obj)

    elif parsed_info["type"] == "CalendarConflictCheck":

        dt_vals = parsed_info["date"].split("-")
        start_dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]), 0, 0, 0)
        start_dt = start_dt + timedelta(hours=int(parsed_info["start_hours"]))
        start_dt = start_dt + timedelta(minutes=int(parsed_info["start_minutes"]))

        end_dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]), 0, 0, 0)
        end_dt = start_dt + timedelta(hours=int(parsed_info["end_hours"]))
        end_dt = start_dt + timedelta(minutes=int(parsed_info["end_minutes"]))

        ret_json = {"success": "1"}
        #ret_json = {}
        #result = Helpers.scheduling_conflict(start_dt, end_dt, parsed_info["identifier"], parsed_info["event_identifier"])
        #if result["success"]:
        #    ret_json = {"success": "1"}
        #else:
        #    ret_json = {"success": "0", "conflict": result["conflicting_event"]}

    elif parsed_info["type"] == "DropCalendarEvent":
        event = CalendarEvent.first(CalendarEvent.identifier == parsed_info["identifier"])
        if not event is None:
            event.key.delete()

    elif parsed_info["type"] == "CreateEventForRep":
        identifier = Helpers.guid()        
        dt_vals = parsed_info["date"].split("-")
        start_dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]), 0, 0, 0)
        start_dt = start_dt + timedelta(hours=int(parsed_info["start_hours"]))
        start_dt = start_dt + timedelta(minutes=int(parsed_info["start_minutes"]))

        end_dt = datetime(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]), 0, 0, 0)
        end_dt = end_dt + timedelta(hours=int(parsed_info["end_hours"]))
        end_dt = end_dt + timedelta(minutes=int(parsed_info["end_minutes"]))

        s = start_dt
        e = end_dt
        idd = identifier

        ev = CalendarEvent(
            identifier=idd,
            field_app_identifier="-1",
            name=parsed_info["name"],
            all_day=False,
            calendar_key=parsed_info["identifier"],
            event_key="custom",
            repeated=False,
            details="",
            color="yellow",
            exception_dates="[]",
            google_series_id="-1",
            owners=json.dumps(["-1"]),
            start_dt=s,
            end_dt=e
        )
        repeated_days_json = []
        if parsed_info["repeats_monday"] == "1":
            repeated_days_json.append(1)
            ev.repeated = True
        if parsed_info["repeats_tuesday"] == "1":
            repeated_days_json.append(2)
            ev.repeated = True
        if parsed_info["repeats_wednesday"] == "1":
            repeated_days_json.append(3)
            ev.repeated = True
        if parsed_info["repeats_thursday"] == "1":
            repeated_days_json.append(4)
            ev.repeated = True
        if parsed_info["repeats_friday"] == "1":
            repeated_days_json.append(5)
            ev.repeated = True
        if parsed_info["repeats_saturday"] == "1":
            repeated_days_json.append(6)
            ev.repeated = True
        if parsed_info["repeats_sunday"] == "1":
            repeated_days_json.append(0)
            ev.repeated = True

        ev.repeated_days = json.dumps(repeated_days_json)
        if ev.repeated:
            ev.start_dt = datetime(2000, 1, 1, s.hour, s.minute)
            ev.end_dt = datetime(2000, 1, 1, e.hour, e.minute)
        ev.put()
        ret_json = {}
        ret_json["identifier"] = ev.identifier
        ret_json["field_app_identifier"] = ev.field_app_identifier
        ret_json["event_key"] = ev.event_key
        ret_json["name"] = ev.name
        ret_json["address"] = ""
        ret_json["phone"] = ""
        ret_json["start_dt"] = str(ev.start_dt).split(".")[0]
        ret_json["end_dt"] = str(ev.end_dt).split(".")[0]

    elif parsed_info["type"] == "CalendarEvents":
        self.response.content_type = "application/json"
        ret_json = []
        user = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["identifier"])
        if not user is None:
            r_id = user.rep_id

            thirty_days_ago = Helpers.pacific_now() + timedelta(days=-30)
            thirty_days_from_now = Helpers.pacific_now() + timedelta(days=30)

            events = CalendarEvent.query(
                ndb.AND(
                    CalendarEvent.start_dt >= thirty_days_ago,
                    CalendarEvent.start_dt <= thirty_days_from_now
                )
            )

            app_ids_to_query = ["-1"]
            app_identifier_idx_dict = {}
            cnt = 0
            for ev in events:
                if ev.calendar_key == user.identifier:
                    obj = {"identifier": ev.identifier}
                    obj["field_app_identifier"] = ev.field_app_identifier
                    obj["event_key"] = ev.event_key
                    obj["name"] = ev.name
                    obj["address"] = ""
                    obj["phone"] = ""
                    obj["start_dt"] = str(ev.start_dt).split(".")[0]
                    obj["end_dt"] = str(ev.end_dt).split(".")[0]
                    app_ids_to_query.append(ev.field_app_identifier)                    
                    if not ev.field_app_identifier == -1:
                        app_ids_to_query.append(ev.field_app_identifier)
                    app_identifier_idx_dict[ev.field_app_identifier] = cnt
                    cnt += 1
                    ret_json.append(obj)

            app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
            for app_entry in app_entries:
                idx = app_identifier_idx_dict[app_entry.identifier]
                ret_json[idx]["address"] = app_entry.customer_address + "\n" + app_entry.customer_city + ", " + app_entry.customer_state + "\n" + app_entry.customer_postal
                ret_json[idx]["phone"] = Helpers.format_phone_number(app_entry.customer_phone)

            repeated_events = CalendarEvent.query(
                ndb.AND(
                    CalendarEvent.calendar_key == parsed_info["identifier"],
                    CalendarEvent.repeated == True
                )
            )
            for ev2 in repeated_events:
                weekdays = json.loads(ev2.repeated_days)
                weekdays_cpy = []
                for weekday in weekdays:
                    if weekday == 0:
                        weekday = 7
                    weekdays_cpy.append(weekday)

                while thirty_days_ago.date() <= thirty_days_from_now.date():
                    if thirty_days_ago.date().isoweekday() in weekdays_cpy:
                        obj = {"identifier": ev2.identifier}
                        obj["field_app_identifier"] = ev2.field_app_identifier
                        obj["event_key"] = ev2.event_key
                        obj["name"] = ev2.name
                        obj["address"] = ""
                        obj["phone"] = ""
                        start_min_str = str(ev2.start_dt.minute)
                        if len(start_min_str) == 1:
                            start_min_str = "0" + start_min_str
                        start_hour_str = str(ev2.start_dt.hour)
                        if len(start_hour_str) == 1:
                            start_hour_str = "0" + start_hour_str
                        start_dt_str = str(thirty_days_ago.date()) + " " + start_hour_str + ":" + start_min_str + ":00"
                        obj["start_dt"] = start_dt_str
                        end_min_str = str(ev2.end_dt.minute)
                        if len(end_min_str) == 1:
                            end_min_str = "0" + end_min_str
                        end_hour_str = str(ev2.end_dt.hour)
                        if len(end_hour_str) == 1:
                            end_hour_str = "0" + end_hour_str
                        end_dt_str = str(thirty_days_ago.date()) + " " + end_hour_str + ":" + end_min_str + ":00"
                        obj["end_dt"] = end_dt_str
                        ret_json.append(obj)

                    thirty_days_ago = thirty_days_ago + timedelta(days=1)
                
            
    elif parsed_info["type"] == "SP2Events":
        ret_json = []
        user = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["identifier"])
        if not user is None:
            r_id = user.rep_id

            self.response.content_type = "application/json"
            ret_json = []

            app_entries = FieldApplicationEntry.query(
                ndb.AND(
                    FieldApplicationEntry.rep_id == r_id,
                    FieldApplicationEntry.archived == False,
                    FieldApplicationEntry.save_me == False
                )
            )

            for app_entry in app_entries:
                obj = {"start_dt": str(app_entry.sp_two_time).split(".")[0]}
                obj["identifier"] = app_entry.identifier
                obj["name"] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
                obj["address"] = app_entry.customer_address + "\n" + app_entry.customer_city + ", " + app_entry.customer_state + "\n" + app_entry.customer_postal
                obj["phone"] = Helpers.format_phone_number(app_entry.customer_phone)
                ret_json.append(obj)

    elif parsed_info["type"] == "QuadrantUpdate":
        quadrant = RepQuadrant.first(RepQuadrant.identifier == parsed_info["quad_id"])
        
        ret_json = []
        if parsed_info["quad_status"] == "active":
            quadrant.active = True
        elif parsed_info["quad_status"]== "deactive":
            quadrant.active = False

        quadrant.modified = Helpers.pacific_now()
        quadrant.put()

        transaction_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "transaction_log_" + quadrant.identifier)
        if not transaction_kv is None:
            items = json.loads(transaction_kv.val)
            msg_status = "reactivated"
            if parsed_info["quad_status"] == "deactive":
                msg_status = "deactivated"
            obj = {"msg": "The region was " + msg_status + "."}
            obj["dt"] = str(quadrant.modified).split(".")[0]
            items.append(obj)
            transaction_kv.val = json.dumps(items)
            transaction_kv.put()

    elif parsed_info["type"] == "QuadrantStatus":
        ret_json = {"active": False}
        quadrant = RepQuadrant.first(RepQuadrant.identifier == parsed_info["quad_id"])
        
        if not quadrant is None:
            ret_json["active"] = quadrant.active
        

    elif parsed_info["type"] == "PinPointMulti":
        ret_json = []

        existing_addresses = []
        existing_pins = PinPoint.query(PinPoint.rep_identifier == parsed_info["rep_identifier"])
        existing_address_identifier_dict = {}
        
        for ep in existing_pins:
            existing_addresses.append(ep.address.lower().strip())
            existing_address_identifier_dict[ep.address.lower().strip()] = ep.identifier

        pins = json.loads(parsed_info["pins"])
        save_list = []
        cnt = 0
        for p in pins:
            if cnt % 50 == 0:
                save_list.append([])

            if not p["address"].lower().strip() in existing_addresses:
                pin_entry = PinPoint(
                    identifier=Helpers.guid(),
                    quadrant_identifier=p["quadrant_identifier"],
                    rep_identifier=p["rep_identifier"],
                    longitude=float(p["longitude"]),
                    latitude=float(p["latitude"]),
                    status=int(p["status"]),
                    address=p["address"],
                    city= p["city"],
                    state=p["state"],
                    postal=p["postal"],
                    homeowner_first=p["homeowner_first"],
                    homeowner_last=p["homeowner_last"],
                    residence_time=p["residence_time"],
                    age_range=p["age_range"],
                    extra_info=p["extra_info"],
                    created=Helpers.pacific_now(),
                    modified=Helpers.pacific_now(),
                    manager_identifier=p["manager_identifier"],
                    is_wp=(p["is_wp"] == "1"),
                )
                ret_json.append(pin_entry.identifier)
                lst = save_list[len(save_list) - 1]
                lst.append(pin_entry)
                cnt += 1
            else:
                ret_json.append(existing_address_identifier_dict[p["address"].lower().strip()])

        for item in save_list:
            if len(item) > 1:
                ndb.put_multi(item)
            elif len(item) == 1:
                item[0].put()


    elif parsed_info["type"] == "RepQuadrantSave":
        import MySQLdb

        now = Helpers.pacific_now()

        self.response.content_type = "application/json"
        ret_json = {"identifier": "-1"}

        quadrant_entry = RepQuadrant(
            identifier= Helpers.guid(),
            rep_identifier=parsed_info["rep_identifier"],
            manager_identifier=parsed_info["manager_identifier"],
            office_identifier=parsed_info["office_identifier"],
            upper_left_lat=float(parsed_info["upper_left_lat"]),
            upper_left_long=float(parsed_info["upper_left_long"]),
            upper_right_lat=float(parsed_info["upper_right_lat"]),
            upper_right_long=float(parsed_info["upper_right_long"]),
            bottom_left_lat=float(parsed_info["bottom_left_lat"]),
            bottom_left_long=float(parsed_info["bottom_left_long"]),
            bottom_right_lat=float(parsed_info["bottom_right_lat"]),
            bottom_right_long=float(parsed_info["bottom_right_long"]),
            all_points=parsed_info["all_points"],
            active=True                
        )
        quadrant_entry.created = now
        quadrant_entry.modified = now

        rep_found = False
        rep = FieldApplicationUser.first(FieldApplicationUser.identifier == quadrant_entry.rep_identifier)
        if not rep is None:
            rep_found = True
            transaction_info = []
            obj = {"msg": "This region was created and assigned to " + rep.first_name.strip().title() + " " + rep.last_name.strip().title()}
            obj["dt"] = str(Helpers.pacific_now()).split(".")[0]
            transaction_info.append(obj)

            transaction_kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="transaction_log_" + quadrant_entry.identifier,
                val=json.dumps(transaction_info),
                expiration=datetime(1970, 1, 1)
            )
            transaction_kv.put()

        time_assigned_kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="quad_time_assigned_" + quadrant_entry.identifier,
            val=str(quadrant_entry.created).split(".")[0],
            expiration=datetime(1970, 1, 1)
        )
        time_assigned_kv.put()

        activity_owner = quadrant_entry.manager_identifier
        if "admin_identifier" in parsed_info.keys():
            activity_owner = parsed_info["admin_identifier"]
        
        if rep_found:
            manager = FieldApplicationUser.first(FieldApplicationUser.identifier == activity_owner)
            msg = manager.first_name.strip().title() + " " + manager.last_name.strip().title() + " created and assigned an area to " + rep.first_name.strip().title() + " " + rep.last_name.strip().title() + "."
            Helpers.log_quadrant_activity(msg)


        if "," in quadrant_entry.all_points:
            key = "manager_saving_quadrant_" + quadrant_entry.manager_identifier
            val = memcache.get(key)
            if val is None:
                memcache.set(key= "manager_saving_quadrant_" + quadrant_entry.manager_identifier, value=parsed_info["all_points"], time=10)                
                quadrant_entry.put()
                parsed_info["quadrant_identifier"] = quadrant_entry.identifier
                taskqueue.add(url="/tq/save_pins", params=parsed_info)            
                ret_json = {"identifier": quadrant_entry.identifier}
                duplicate_zone = False

        ret_json = {"identifier": quadrant_entry.identifier}
                
    elif parsed_info["type"] == "UpdatePin":
        logging.info("in Updated PIN")
        point = PinPoint.first(PinPoint.identifier == "NewPower")
        logging.info(point)
        if point is not None:
            point.age_range = "changed"
            logging.info("Updated")
        point.put() 
    
    elif parsed_info["type"] == "ClockInClockOutStatus":
        today = Helpers.pacific_today()
        ret_json = {"clocked_in": 0}
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "clock_ins_clock_outs_" + str(today) + "_" + parsed_info["identifier"])
        if not kv is None:
            items = json.loads(kv.val)
            if len(items) > 0:
                last_item = items[len(items) - 1]
                if last_item["status"] == "in":
                    ret_json["clocked_in"] = 1
        

    elif parsed_info["type"] == "RepsInOffice":
        identifier = parsed_info["identifier"]
        #reps = FieldApplicationUser.query()
        reps = FieldApplicationUser.query(
            ndb.AND(
                FieldApplicationUser.current_status == 0,
                FieldApplicationUser.main_office == identifier,
                FieldApplicationUser.user_type.IN(["field", "asst_mgr", "co_mgr", "sales_dist_mgr", "rg_mgr", "solar_pro", "solar_pro_manager", "energy_expert", "sales_manager"])
            )
        )
        ret_json = []
        for rep in reps:
            ret_json.append({"identifier": rep.identifier, "first_name": rep.first_name.strip().title(), "last_name": rep.last_name.strip().title(), "name": rep.first_name.strip().title() + " " + rep.last_name.strip().title(), "phone": rep.rep_phone, "phone_formatted": Helpers.format_phone_number(rep.rep_phone), "rep_id": rep.rep_id, "registration_date": str(rep.registration_date), "user_type": rep.user_type})

    elif parsed_info["type"] == "UpdatePinStatus":
        pin = PinPoint.first(PinPoint.identifier == parsed_info["identifier"])
        if not pin is None:
            pin.status = int(parsed_info["status"])
            pin.modified = Helpers.pacific_now()
            pin.put()

            pin_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "last_pin_status_" + pin.identifier)
            if pin_kv is None:
                pin_kv = KeyValueStoreItem(
                    identifier=Helpers.guid(),
                    keyy="last_pin_status_" + pin.identifier,
                    expiration=datetime(1970, 1, 1)
                )
            pin_kv.val = parsed_info["status"]
            pin_kv.put()

            put = False
            pin_kv2 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "last_pin_status_rep_" + pin.identifier)
            if pin_kv2 is None:
                pin_kv2 = KeyValueStoreItem(
                    identifier=Helpers.guid(),
                    keyy="last_pin_status_rep_" + pin.identifier,
                    expiration=datetime(1970, 1, 1)
                )
            rep = FieldApplicationUser.first(FieldApplicationUser.identifier == pin.rep_identifier)
            if not rep is None:
                put = True
                pin_kv2.val = pin.rep_identifier
                
            if put:
                pin_kv2.put()

            quadrant = RepQuadrant.first(RepQuadrant.identifier == pin.quadrant_identifier)
            if not quadrant is None:
                quadrant.modified = Helpers.pacific_now()
                quadrant.put()

            atts = ["identifier",
            "quadrant_identifier",
            "rep_identifier",
            "longitude",
            "latitude",
            "status",
            "extra_info",
            "created",
            "modified"]
            

            item = {}            
            for att in atts:
                attribute = getattr(pin, att)
                if att in ["created", "modified"]:
                    attribute = str(attribute)
                    attribute = attribute.split(".")[0]
                # if att == "extra_info":
                #     att = json.loads(attribute)
                item[att] = attribute
            ret_json = item

    elif parsed_info["type"] == "SalesFormPassOfSave":
        guid = Helpers.guid()
        kv1 = KeyValueStoreItem(
            identifier=guid,
            keyy="pass_off_login_" + guid,
            val=parsed_info["identifier"],
            expiration=Helpers.pacific_now() + timedelta(hours=1)
        )
        kv2 = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="pass_off_info_" + guid,
            val=parsed_info["info"],
            expiration=Helpers.pacific_now() + timedelta(hours=1)
        )
        kv1.put()
        kv2.put()
        ret_json = {"token": guid}

    elif parsed_info["type"] == "GridQuery":
        ret_json = []
        quadrant = RepQuadrant.first(RepQuadrant.identifier == parsed_info["identifier"])
        if not quadrant is None:
            ret_json = json.loads(quadrant.all_points)

    elif parsed_info["type"] == "PinsInPolygon":
        ret_json = []
        import MySQLdb
        db = Helpers.connect_to_cloud_sql()
        cursor = db.cursor()
        cursor.execute("USE addresses;")
        sql = "SELECT ST_AsText(coordinates) FROM points WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(("        
        points = json.loads(parsed_info["coordinates"])
        for point in (points + [points[0]]):
            sql += (point["latitude"] + " " + point["longitude"] + ", ")
        sql = sql[0:len(sql) - 2]
        sql += "))'), points.coordinates);"

        for row in cursor.fetchall():
            pt_str = row[0]
            pt_str_vals = pt_str.split(" ")
            lat = pt_str_vals[0].replace("POINT(", "")
            lng = pt_str_vals[1].replace(")", "")
            ret_json.append(lat + "," + lng)

        cursor.close()
        db.close()

    elif parsed_info["type"] == "ReassignQuadrant":
        self.response.content_type = "application/json"
        ret_json = {"reassigned": "0"}
        quadrant = RepQuadrant.first(RepQuadrant.identifier == parsed_info["identifier"])
        if not quadrant is None:
            quadrant.rep_identifier = parsed_info["rep_identifier"]
            quadrant.modified = Helpers.pacific_now()
            quadrant.put()
            ret_json["reassigned"] = "1"

            transaction_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "transaction_log_" + quadrant.identifier)
            if not transaction_kv is None:
                rep = FieldApplicationUser.first(FieldApplicationUser.identifier == quadrant.rep_identifier)
                if not rep is None:
                    items = json.loads(transaction_kv.val)
                    obj = {"msg": "The region was reassigned to " + rep.first_name.strip().title() + " " + rep.last_name.strip().title() + "."}
                    obj["dt"] = str(Helpers.pacific_now()).split(".")[0]
                    items.append(obj)
                    transaction_kv.val = json.dumps(items)
                    transaction_kv.put()

            time_assigned_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "quad_time_assigned_" + quadrant.identifier)
            if not time_assigned_kv is None:
                time_assigned_kv.val = str(quadrant.modified).split(".")[0]
                time_assigned_kv.put()

            logging_identifier = None
            if "manager_identifier" in parsed_info.keys():
                logging_identifier = parsed_info["manager_identifier"]
            if "admin_identifier" in parsed_info.keys():
                logging_identifier = parsed_info["admin_identifier"]

            rep = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["rep_identifier"])
            if not rep is None:
                if not logging_identifier is None:
                    activity_user = FieldApplicationUser.first(FieldApplicationUser.identifier == logging_identifier)
                    if not activity_user is None:
                        msg = activity_user.first_name.strip().title() + " " + activity_user.last_name.strip().title() + " reassigned a region to " + rep.first_name.strip().title() + " " + rep.last_name.strip().title() + "."
                        Helpers.log_quadrant_activity(msg)

            taskqueue.add(url="/tq/reassign_pins", params={"identifier": quadrant.identifier, "new_rep_identifier": parsed_info["rep_identifier"]})

    elif parsed_info["type"] == "PinQuery":
        active_identifiers = ["-1"]
        active_quadrants = RepQuadrant.query(
            ndb.AND(
                RepQuadrant.rep_identifier == parsed_info["identifier"],
                RepQuadrant.active == True
            )
        )

        for active_quadrant in active_quadrants:
            active_identifiers.append(active_quadrant.identifier)
        
        points = PinPoint.query(PinPoint.quadrant_identifier.IN(active_identifiers))
        
        ret_json = []
        atts = ["identifier",
            "quadrant_identifier",
            "rep_identifier",
            "longitude",
            "latitude",
            "status",
            "extra_info",
            "created",
            "modified"]
        for p in points:
            item = {}
            for att in atts:
                attribute = getattr(p, att)
                if att in ["created", "modified"]:
                    attribute = str(attribute)
                    attribute = attribute.split(".")[0]
                # if att == "extra_info":
                #     att = json.loads(attribute)
                item[att] = attribute
            ret_json.append(item)

    elif parsed_info["type"] == "PullPinNotes":
        ret_json = {"notes": "Nothing recorded yet..."}
        note_obj = PinNote.first(PinNote.pin_identifier == parsed_info["identifier"])
        if not note_obj is None:
            ret_json["notes"] = note_obj.notes

        ret_json["last_known_status_date"] = "01/01/1970"
        status = "Unchanged"
        last_rep_touched = ""
        pin_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "last_pin_status_" + parsed_info["identifier"])
        if not pin_kv is None:
            status_mapping = {"0": "CD", "1": "R", "2": "Unchanged", "3": "CB", "4": "NQ", "5": "NI", "6": "AB"}
            if str(pin_kv.val) in status_mapping.keys():
                status = status_mapping[str(pin_kv.val)]
                
                month_value = str(pin_kv.modified.month)
                day_value = str(pin_kv.modified.day)

                if len(month_value) == 1:
                    month_value = "0" + month_value
                if len(day_value) == 1:
                    day_value = "0" + day_value

                ret_json["last_known_status_date"] = month_value + "/" + day_value + "/" + str(pin_kv.modified.year) 


        ret_json["last_known_status"] = status
        pin_kv2 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "last_pin_status_rep_" + parsed_info["identifier"])
        if not pin_kv2 is None:
            rep = FieldApplicationUser.first(FieldApplicationUser.identifier == pin_kv2.val)
            if not rep is None:
                last_rep_touched = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
        ret_json["last_rep_touched"] = last_rep_touched

    elif parsed_info["type"] == "SavePinNotes":
        note_obj = PinNote.first(PinNote.pin_identifier == parsed_info["identifier"])
        if note_obj is None:
            note_obj = PinNote(
                identifier=Helpers.guid(),
                pin_identifier=parsed_info["identifier"],                
            )
        note_obj.notes = parsed_info["notes"]
        note_obj.put()

    elif parsed_info["type"] == "DropQuadrant":
        quadrant = RepQuadrant.first(RepQuadrant.identifier == parsed_info["identifier"])
        if not quadrant is None:
            quadrant.key.delete()

            pins_to_delete = []
            pins = PinPoint.query(PinPoint.quadrant_identifier == parsed_info["identifier"])
            pin_identifiers = ["-1"]
            for pin in pins:
                pin_identifiers.append(pin.identifier)
                pins_to_delete.append(pin.key)

            ndb.delete_multi(pins_to_delete)

            notes_to_delete = []

            notes = PinNote.query(PinNote.pin_identifier.IN(pin_identifiers))
            for note in notes:
                notes_to_delete.append(note.key)

            ndb.delete_multi(notes_to_delete)

            ret_json = {"finished": "1"}

    elif parsed_info["type"] == "QuadrantBoundsUpdate":
        self.response.content_type = "application/json"
        ret_json = {"identifier": parsed_info["identifier"]}
        quadrant = RepQuadrant.first(RepQuadrant.identifier == parsed_info["identifier"])
        if not quadrant is None:
            quadrant.upper_left_lat = float(parsed_info["upper_left_lat"])
            quadrant.upper_left_long = float(parsed_info["upper_left_long"])
            quadrant.upper_right_lat = float(parsed_info["upper_right_lat"])
            quadrant.upper_right_long = float(parsed_info["upper_right_long"])
            quadrant.bottom_left_lat = float(parsed_info["bottom_left_lat"])
            quadrant.bottom_left_long = float(parsed_info["bottom_left_long"])
            quadrant.bottom_right_lat = float(parsed_info["bottom_right_lat"])
            bottom_right_long=float(parsed_info["bottom_right_long"])
            quadrant.all_points = parsed_info["all_points"]
            quadrant.put()

            transaction_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "transaction_log_" + quadrant.identifier)
            if not transaction_kv is None:
                items = json.loads(transaction_kv.val)
                obj = {"msg": "The region's bounds were redrawn"}
                obj["dt"] = str(Helpers.pacific_now()).split(".")[0]
                items.append(obj)
                transaction_kv.val = json.dumps(items)
                transaction_kv.put()

            taskqueue.add(url="/tq/bounds_update", params={"identifier": quadrant.identifier, "all_points": quadrant.all_points})

    elif parsed_info["type"] == "LocationLog":
        item = UserLocationLogItem(
            identifier=Helpers.guid(),
            rep_identifier=parsed_info["identifier"],
            latitude=float(parsed_info["latitude"]),
            longitude=float(parsed_info["longitude"]),
            pin_latitude=float(parsed_info["pin_latitude"]),
            pin_longitude=float(parsed_info["pin_longitude"]),
            in_bounds=(parsed_info["in_bounds"] == "1"),
            created=Helpers.pacific_now()
        )
        item.put()
        in_bounds = item.in_bounds

        if in_bounds:
            rep = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["identifier"])
            if not rep is None:
                existing_stat_found = False
                h_p_n = Helpers.pacific_now()
                stats = LeaderBoardStat.query(
                    ndb.AND(
                        LeaderBoardStat.metric_key == "app_stat_clockins",
                        LeaderBoardStat.dt >= datetime(h_p_n.year, h_p_n.month, h_p_n.day, 0, 0, 0)
                    )
                )
                for stat in stats:
                    if stat.rep_id == rep.rep_id:
                        existing_stat_found = True

                if not existing_stat_found:
                    stat = LeaderBoardStat(
                        identifier=Helpers.guid(),
                        rep_id=rep.rep_id,                    
                        office_identifier=rep.main_office,
                        field_app_identifier="-1",
                        in_bounds=True,
                        pin_identifier="-1",
                        metric_key="app_stat_clockins",
                        dt=datetime(h_p_n.year, h_p_n.month, h_p_n.day, h_p_n.hour, h_p_n.minute, h_p_n.second)
                    )
                    stat.put()

    elif parsed_info["type"] == "ClockOut":
        now = Helpers.pacific_now()
        today = now.date()
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "clock_ins_clock_outs_" + str(today) + "_" + parsed_info["identifier"])
        if kv is None:
            kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="clock_ins_clock_outs_" + str(today) + "_" + parsed_info["identifier"],
                val="[]",
                expiration=now + timedelta(days=7)
            )
        items = json.loads(kv.val)
        if len(items) == 0:
            items.append({"status": "out", "dt": str(now).split(".")[0]})
        elif items[len(items) - 1]["status"] == "in":
            items.append({"status": "out", "dt": str(now).split(".")[0]})
        kv.val = json.dumps(items)
        kv.put()
            
    elif parsed_info["type"] == "ClockIn":
        now = Helpers.pacific_now()
        today = now.date()
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "clock_ins_clock_outs_" + str(today) + "_" + parsed_info["identifier"])
        if kv is None:
            kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="clock_ins_clock_outs_" + str(today) + "_" + parsed_info["identifier"],
                val="[]",
                expiration=now + timedelta(days=7)
            )
        items = json.loads(kv.val)
        if len(items) == 0:
            items.append({"status": "in", "dt": str(now).split(".")[0]})
        elif items[len(items) - 1]["status"] == "out":
            items.append({"status": "in", "dt": str(now).split(".")[0]})

        kv.val = json.dumps(items)
        kv.put()

    elif parsed_info["type"] == "KnockingStatus":
        ret_json = {}
        kh = UserKnockedHours.first(UserKnockedHours.rep_identifier == parsed_info["identifier"])
        if kh is not None:
            ret_json["clocked_in"] = kh.clocked_in
        else:
            ret_json["clocked_in"] = False
            

    elif parsed_info["type"] == "knocked_hours":
        ret_json = {"knocked_hours_daily": float(0), "knocked_hours_weekly": float(0)}
        kh = UserKnockedHours.first(UserKnockedHours.rep_identifier == parsed_info["identifier"])
        if kh is not None:
            ret_json["knocked_hours_daily"] = kh.knocked_hours_daily
            ret_json["knocked_hours_weekly"] = kh.knocked_hours_weekly            

    elif parsed_info["type"] == "AutoClockOut":
        taskqueue.add(url="/tq/auto_clock_out", params={})
        


    elif parsed_info["type"] == "reset_weekly_hours":
        user_identifiers_to_query = ["-1"]
        users = FieldApplicationUser.query(FieldApplicationUser.current_status == 0)
        for user in users:
            user_identifiers_to_query.append(user.identifier)

        users_to_save = []
        user_clocked_in = UserKnockedHours.query(UserKnockedHours.clocked_in == False)
        for user in user_clocked_in:
            user.knocked_hours_weekly = 0
            users_to_save.append(user)

        if len(users_to_save) == 1:
            users_to_save[0].put()
        elif len(users_to_save) > 1:
            ndb.put_multi(users_to_save)

    elif parsed_info["type"] == "reset_daily_hours":
        user_identifiers_to_query = ["-1"]
        users = FieldApplicationUser.query(FieldApplicationUser.current_status == 0)
        for user in users:
            user_identifiers_to_query.append(user.identifier)

        users_to_save = []
        user_clocked_in = UserKnockedHours.query(UserKnockedHours.clocked_in == False)
        for user in user_clocked_in:
            user.knocked_hours_daily = 0
            users_to_save.append(user)

        if len(users_to_save) == 1:
            users_to_save[0].put()
        elif len(users_to_save) > 1:
            ndb.put_multi(users_to_save)
                
    elif parsed_info["type"] == "WhitePagesData":
        item = WhitePagesData(
            identifier=Helpers.guid(),
            is_valid="",
            street_line_1="",
            street_line_2="",
            city="",
            zip4="",
            state_code="",
            country_code="",
            is_active="",
            last_sale_date="",
            total_value="",
            owner_first="",
            owner_last="",
            age_range="",
            latitude=float(parsed_info["latitude"]),
            longitude=float(parsed_info["longitude"]),
        )
        item.put()

    elif parsed_info["type"] == "StartKnockingBoundsCheck":
        import MySQLdb
        db = Helpers.connect_to_cloud_sql()
        cursor = db.cursor()
        cursor.execute("USE addresses;")
        ret_json = {"success": False}

        quadrants = RepQuadrant.query(
            ndb.AND(
                RepQuadrant.rep_identifier == parsed_info["identifier"],
                RepQuadrant.active == True
            )
        )
        if quadrants.count() > 0:
            sql = ""
            quadrant_count = 1
            for quadrant in quadrants:
                sel_text = ""
                if quadrant_count == 1:
                    sel_text = "SELECT "
                sql += (sel_text + "ST_Distance(ST_GeomFromText('Polygon((")
                ret_json["success"] = True
                points = json.loads(quadrant.all_points)
                for point in (points + [points[0]]):
                    lat = point.split(",")[0]
                    lng = point.split(",")[1]
                    sql += (lat + " " + lng + ",")
                sql = sql[0:len(sql) - 1]
                sql += "))'), Point("
                sql += parsed_info["latitude"]
                sql += ","
                sql += parsed_info["longitude"]
                sql += ")) AS distance"
                sql += str(quadrant_count)
                sql += ", "
                quadrant_count += 1

            sql = sql[0:len(sql) - 2]
            sql = sql.strip()
            query = cursor.execute(sql)

            distances = []
            rows_copy = []
            column_count = quadrant_count - 1
            idx = 0
            for row in cursor.fetchall():
                dct = {}
                while idx < column_count:
                    dct["distance" + str(idx + 1)] = row[idx]
                    idx += 1
                rows_copy.append(dct)            

            for row in rows_copy:
                keys = row.keys()
                for key in keys:
                    distances.append(float(row[key]))
                quadrant_count += 1
            
            distances.sort()
            if len(distances) > 0:
                min_distance = distances[0]
                if min_distance > 0.005:
                    ret_json["success"] = False

        cursor.close()
        db.close()

    elif parsed_info["type"] == "AppStatLB":
        stat_mapping = {"0": "app_stat_CD", "1": "app_stat_R", "3": "app_stat_CB", "4": "app_stat_NQ", "5": "app_stat_NI", "6": "app_stat_AB", "7": "app_stat_NH"}
        ret_json = {}
        rep = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["rep_identifier"])
        if not rep is None:
            stat = LeaderBoardStat.first(LeaderBoardStat.pin_identifier == parsed_info["identifier"])
            if stat is None:
                stat = LeaderBoardStat(
                    identifier=Helpers.guid(),
                    rep_id=parsed_info["rep_id"],                    
                    office_identifier=rep.main_office,
                    field_app_identifier="-1",
                    in_bounds=(parsed_info["in_bounds"] == "1"),
                    pin_identifier=parsed_info["identifier"]
                )

            stat.metric_key = stat_mapping[parsed_info["status"]]
            stat.dt = Helpers.pacific_now()
            stat.put()

    elif parsed_info["type"] == "RecordOneOnOne":
        start_date_vals = parsed_info["start"].split(" ")[0].split("-")
        start_time_vals = parsed_info["start"].split(" ")[1].split(":")
        o = OneOnOne(
            identifier=Helpers.guid(),
            created=Helpers.pacific_now(),
            start_time=datetime(int(start_date_vals[0]), int(start_date_vals[1]), int(start_date_vals[2]), int(start_time_vals[0]), int(start_time_vals[1]), int(start_time_vals[2])),
            stop_time=Helpers.pacific_now(),
            modified=Helpers.pacific_now(),
            manager_identifier=parsed_info["manager_identifier"],
            rep_identifier=parsed_info["rep_identifier"],
            office_identifier=parsed_info["office_identifier"],
            notes=json.dumps({"notes": parsed_info["notes"], "title": parsed_info["training_topic"]})
        )
        o.put()

        stat = LeaderBoardStat(
            identifier=Helpers.guid(),
            metric_key="app_stat_one_on_one",
            rep_id=parsed_info["rep_id"],                    
            office_identifier=parsed_info["office_identifier"],
            field_app_identifier=parsed_info["rep_identifier"],
            in_bounds=True,
            pin_identifier="-1",
            dt=Helpers.pacific_now()
        )
        stat.put()

    elif parsed_info["type"] == "CheckRepOneOnOneConfirmationStatus":
        ret_json = {"ready": False}
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == parsed_info["identifier"] + "_one_on_one_status")
        if not kv is None:
            if kv.val == "session_started":
                ret_json["ready"] = True

    elif parsed_info["type"] == "OneOnOneLocationFraudWarning":
        rep1 = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["identifier_1"])
        if not rep1 is None:
            rep2 = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["identifier_2"])
            if not rep2 is None:
                notification = Notification.first(Notification.action_name == "NP Grid 1:1 Location Fraud")
                if not notification is None:
                    subject = "NP Grid One-On-One Warning"
                    msg = rep1.first_name.strip().title() + " " + rep1.last_name.strip().title() + " and " + rep2.first_name.strip().title() + " " + rep2.last_name.strip().title() + " have tried to start a one-on-one session when the distance between them was greater than 0.25 miles"
                    for p in notification.notification_list:
                        Helpers.send_email(p.email_address, subject, msg)

    elif parsed_info["type"] == "PacificTime":
        ret_json = {"time": str(Helpers.pacific_now()).split(".")[0]}

    elif parsed_info["type"] == "SaveKnockingMeeting":
        meeting_info = {"attendance": json.loads(parsed_info["attendance_json"])}
        start_dt = datetime(int(parsed_info["start_year"]), int(parsed_info["start_month"]), int(parsed_info["start_day"]), int(parsed_info["start_hour"]), int(parsed_info["start_minute"]), int(parsed_info["start_second"]))

        existing_meetings = KnockingMeeting.query(
            ndb.AND(
                KnockingMeeting.start_time >= datetime(start_dt.year, start_dt.month, start_dt.day),
                KnockingMeeting.start_time <= datetime(start_dt.year, start_dt.month, start_dt.day, 23, 59, 59)
            )
        )
        found = False

        for existing_meeting in existing_meetings:
            if existing_meeting.manager_identifier == parsed_info["identifier"]:
                found = True

        manager = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["identifier"])
        if not manager is None:
            meeting = KnockingMeeting(
                identifier=Helpers.guid(),
                manager_identifier=parsed_info["identifier"],
                start_time=start_dt,
                stop_time=Helpers.pacific_now(),
                info=json.dumps(meeting_info)
            )
            meeting.put()

            rep_identifiers_to_query = ["-1"]
            for identifier in meeting_info["attendance"].keys():
                rep_identifiers_to_query.append(identifier)

            rep_identifier_rep_id_dict = {}
            reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_identifiers_to_query))
            for rep in reps:
                rep_identifier_rep_id_dict[rep.identifier] = rep.rep_id

            stats_to_put = []
            stat_metric_key_mapping = {"absent": "app_stat_knocking_meeting_absent", "late": "app_stat_knocking_meeting_late", "present": "app_stat_knocking_meeting_present"}
            for rep_identifier in rep_identifier_rep_id_dict.keys():
                stat = LeaderBoardStat(
                    identifier=Helpers.guid(),
                    rep_id=rep_identifier_rep_id_dict[rep_identifier],
                    dt=Helpers.pacific_now(),
                    metric_key=stat_metric_key_mapping[meeting_info["attendance"][rep_identifier]],
                    office_identifier=manager.main_office,
                    field_app_identifier="-1",
                    in_bounds=True,
                    pin_identifier="-1"
                )
                stats_to_put.append(stat)

            if not found:
                manager_stat = LeaderBoardStat(
                    identifier=Helpers.guid(),
                    rep_id=manager.rep_id,
                    dt=Helpers.pacific_now(),
                    metric_key="app_stat_knocking_meeting_held",
                    office_identifier=manager.main_office,
                    field_app_identifier="-1",
                    in_bounds=True,
                    pin_identifier="-1"
                )
                stats_to_put.append(manager_stat)

            if len(stats_to_put) == 1:
                stats_to_put[0].put()
            elif len(stats_to_put) > 1:
                ndb.put_multi(stats_to_put)

    elif parsed_info["type"] == "GoalCheck":
        ret_json = {"prompt": False, "last_week_start": "1970-01-01"}
        h_p_t = Helpers.pacific_today()
        if h_p_t.isoweekday() == 6:
            h_p_n = Helpers.pacific_now()
            if h_p_n.hour >= 18:
                h_p_n = h_p_n + timedelta(days=1)
                h_p_t = h_p_n.date()
                
        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        start_dt = start_dt + timedelta(days=-7)
        end_dt = end_dt + timedelta(days=-7)

        goal = RepGoal.first(
            ndb.AND(
                RepGoal.start_date >= start_dt.date(),
                RepGoal.rep_identifier == parsed_info["identifier"]
            )
        )
        if goal is None:
            ret_json["prompt"] = True
            ret_json["last_week_start"] = str(start_dt.date())
            ret_json["last_week_end"] = str(end_dt.date())

    elif parsed_info["type"] == "GoalSave":
        start_date_vals = parsed_info["start_date"].split("-")
        start_dt = datetime(int(start_date_vals[0]), int(start_date_vals[1]), int(start_date_vals[2]))
        end_dt = datetime(int(start_date_vals[0]), int(start_date_vals[1]), int(start_date_vals[2])) + timedelta(days=7)
        end_dt = end_dt + timedelta(hours=-1)
        g_info = {"HK": int(parsed_info["HK"]), "QC": int(parsed_info["QC"]), "AC": int(parsed_info["AC"]), "AK": int(parsed_info["AK"]), "CD": int(parsed_info["CD"])}
        goal = RepGoal(
            identifier=Helpers.guid(),
            rep_identifier=parsed_info["identifier"],
            start_date=start_dt.date(),
            end_date=end_dt.date(),
            goal_info=json.dumps(g_info)
        )
        goal.put()

    elif parsed_info["type"] == "RecordPhoneCall":
        rep = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["identifier"])
        if not rep is None:
            stat = LeaderBoardStat(
                identifier=Helpers.guid(),
                rep_id=rep.rep_id,                    
                office_identifier=rep.main_office,
                field_app_identifier=parsed_info["callee"],
                in_bounds=True,
                pin_identifier="-1",
                metric_key="app_stat_phone_call",
                dt=Helpers.pacific_now()
            )
            stat.put()

    elif parsed_info["type"] == "ConfirmOneOnOneSession":
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == parsed_info["identifier"] + "_one_on_one_status")
        if not kv is None:
            kv.val = "session_started"
            kv.put()

    elif parsed_info["type"] == "OneOnOneManagerLocationCheck":
        ret_json = {"latitude": -500.0, "longitude": -500.0}
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == parsed_info["identifier"] + "_one_on_one_manager_location")
        if not kv is None:
            ret_json = json.loads(kv.val)

    elif parsed_info["type"] == "OneOnOneSessionCodeCheck":
        ret_json = {"success": False}
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == parsed_info["identifier"] + "_one_on_one_code")
        if not kv is None:
            if kv.val == parsed_info["code"]:
                ret_json["success"] = True

    elif parsed_info["type"] == "GetOneOnOneManagerIdentifierFromRepIdentifier":
        ret_json = {"identifier": "-1"}
        kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == parsed_info["rep_identifier"] + "_one_on_one_current_manager")
        if not kv is None:
            ret_json["identifier"] = kv.val

    elif parsed_info["type"] == "OneOnOneStartSessionAttempt":
        kv1 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == parsed_info["rep_identifier"] + "_one_on_one_code")
        if kv1 is None:
            kv1 = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy=parsed_info["rep_identifier"] + "_one_on_one_code",
            )
        kv1.val = str(parsed_info["code"])
        kv1.expiration = Helpers.pacific_now() + timedelta(hours=1)
        
        kv2 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == parsed_info["rep_identifier"] + "_one_on_one_manager_location")
        if kv2 is None:
            kv2 = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy=parsed_info["rep_identifier"] + "_one_on_one_manager_location"
            )
        kv2.val = json.dumps({"latitude": parsed_info["latitude"], "longitude": parsed_info["longitude"]})
        kv2.expiration = Helpers.pacific_now() + timedelta(hours=1)

        kv3 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == parsed_info["rep_identifier"] + "_one_on_one_status")
        if kv3 is None:
            kv3 = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy=parsed_info["rep_identifier"] + "_one_on_one_status"
            )
        kv3.val = "awaiting_rep"
        kv3.expiration = Helpers.pacific_now() + timedelta(hours=1)

        kv4 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == parsed_info["rep_identifier"] + "_one_on_one_current_manager")
        if kv4 is None:
            kv4 = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy=parsed_info["rep_identifier"] + "_one_on_one_current_manager"
            )
        kv4.val = parsed_info["manager_identifier"]
        kv4.expiration = Helpers.pacific_now() + timedelta(hours=1)

        for kv in [kv1, kv2, kv3, kv4]:
            kv.put()

    elif parsed_info["type"] == "ToolsStats":
        ret_json = {}
        ret_json["phone_calls"] = 0
        ret_json["phone_calls_data"] = []
        ret_json["one_on_ones"] = 0
        ret_json["one_on_ones_data"] = []
        ret_json["one_on_one_details"] = []
        ret_json["session_override_password"] = "-1"
        ret_json["yesterday_abs"] = {}
        ret_json["this_week_abs"] = {}
        ret_json["this_week_hks"] = {}
        ret_json["this_week_ab_goals"] = {}
        ret_json["office_lat"] = ""
        ret_json["office_lng"] = ""
        ret_json["this_week_ab_tally"] = 0
        ret_json["this_week_cd_tally"] = 0
        ret_json["this_week_ak_tally"] = 0
        ret_json["this_week_ab_progress"] = "100%"
        ret_json["this_week_cd_progress"] = "100%"
        ret_json["this_week_ak_progress"] = "100%"
        ret_json["this_week_ab_goal"] = 0
        ret_json["this_week_cd_goal"] = 0
        ret_json["this_week_ak_goal"] = 0

        passwords = Helpers.read_setting("passwords")
        for p in passwords:
            if p["name"] == "One on One Session Override Code":
                ret_json["session_override_password"] = p["password"]

        h_p_t = Helpers.pacific_today()
        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key.IN(["app_stat_phone_call", "app_stat_one_on_one"]),
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= Helpers.pacific_now(),
                LeaderBoardStat.office_identifier == parsed_info["office_identifier"]
            )
        )

        rep_ids_to_query = ["-1"]
        metric_key_return_json_mapping = {"app_stat_phone_call": "phone_calls", "app_stat_one_on_one": "one_on_ones"}
        for stat in stats:
            if stat.rep_id == parsed_info["rep_id"]:
                ret_json[metric_key_return_json_mapping[stat.metric_key]] += 1
                ret_json[metric_key_return_json_mapping[stat.metric_key] + "_data"].append(stat.field_app_identifier)

        rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == parsed_info["rep_id"])
        if not rep is None:
            if rep.is_manager or True:
                office = OfficeLocation.first(OfficeLocation.identifier == parsed_info["office_identifier"])
                if not office is None:
                    geo_data = json.loads(office.geo_data)
                    ret_json["office_lat"] = geo_data[0].split(",")[0]
                    ret_json["office_lng"] = geo_data[0].split(",")[1]

                one_on_ones = OneOnOne.query(OneOnOne.stop_time >= Helpers.pacific_now() + timedelta(days=-21))
                for o in one_on_ones:
                    if o.manager_identifier == parsed_info["manager_identifier"]:
                        n = json.loads(o.notes)
                        ret_json["one_on_one_details"].append({"dt": o.stop_time.date(), "notes": {"title": n["title"], "notes": n["notes"]}, "identifier": o.identifier, "rep_identifier": o.rep_identifier})

                users = FieldApplicationUser.query(
                    ndb.AND(
                        FieldApplicationUser.current_status == 0,
                        FieldApplicationUser.main_office == parsed_info["office_identifier"]
                    )
                )
                rep_id_rep_identifier_dict = {}
                rep_identifier_rep_id_dict = {}
                for user in users:
                    rep_id_rep_identifier_dict[user.rep_id] = user.identifier
                    rep_identifier_rep_id_dict[user.identifier] = user.rep_id
                    ret_json["yesterday_abs"][user.rep_id] = 0
                    ret_json["this_week_abs"][user.rep_id] = 0
                    ret_json["this_week_hks"][user.rep_id] = 0
                    ret_json["this_week_ab_goals"][user.rep_id] = 0
                    
                h_p_t = Helpers.pacific_today()
                start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day) + timedelta(days=-1)
                end_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day) + timedelta(seconds=-1)

                lb_stats = LeaderBoardStat.query(
                    ndb.AND(
                        LeaderBoardStat.metric_key == "leads_acquired",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt,
                        LeaderBoardStat.office_identifier == parsed_info["office_identifier"]
                    )
                )

                for stat in lb_stats:
                    if stat.rep_id in ret_json["yesterday_abs"].keys():
                        ret_json["yesterday_abs"][stat.rep_id] += 1

                start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
                while not start_dt.isoweekday() == 7:
                    start_dt = start_dt + timedelta(days=-1)

                start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
                end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
                end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

                lb_stats = LeaderBoardStat.query(
                    ndb.AND(
                        LeaderBoardStat.metric_key == "leads_acquired",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt,
                        LeaderBoardStat.office_identifier == parsed_info["office_identifier"]
                    )
                )

                for stat in lb_stats:
                    if stat.rep_id in ret_json["this_week_abs"].keys():
                        ret_json["this_week_abs"][stat.rep_id] += 1
                    ret_json["this_week_ab_tally"] += 1

                lb_stats = LeaderBoardStat.query(
                    ndb.AND(
                        LeaderBoardStat.metric_key == "packets_submitted",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt,
                        LeaderBoardStat.office_identifier == parsed_info["office_identifier"]
                    )
                )
            

                for stat in lb_stats:
                    ret_json["this_week_cd_tally"] += 1

                rep_ids_to_query5 = ["-1"]
                rep_id_ak_tally_dict = {}
                lb_stats = LeaderBoardStat.query(
                    ndb.AND(
                        LeaderBoardStat.metric_key == "appointments_kept",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt,
                        LeaderBoardStat.office_identifier == parsed_info["office_identifier"]
                    )
                )

                for stat in lb_stats:
                    if not stat.rep_id in rep_ids_to_query5:
                        rep_ids_to_query5.append(stat.rep_id)
                    if not stat.rep_id in rep_id_ak_tally_dict.keys():
                        rep_id_ak_tally_dict[stat.rep_id] = 0
                    rep_id_ak_tally_dict[stat.rep_id] += 1

                solar_pros5 = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query5))
                for sp in solar_pros5:
                    if sp.user_type in ["solar_pro", "solar_pro_manager"]:
                        ret_json["this_week_ak_tally"] += rep_id_ak_tally_dict[sp.rep_id]

                week_start_dt = Helpers.pacific_now()
                while not week_start_dt.isoweekday() == 7:
                    week_start_dt = week_start_dt + timedelta(days=-1)

                ab_divide_by = 0
                cd_divide_by = 0
                ak_divide_by = 0
                dinner_goal_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "dinner_goals_" + str(week_start_dt.date()).replace("-", "_") + "_" + parsed_info["office_identifier"])
                if not dinner_goal_kv is None:
                    dinner_info = json.loads(dinner_goal_kv.val)
                    ab_divide_by = dinner_info["AB"]
                    cd_divide_by = dinner_info["CD"]
                    ak_divide_by = dinner_info["AK"]

                ret_json["this_week_ab_goal"] = ab_divide_by
                ret_json["this_week_cd_goal"] = cd_divide_by
                ret_json["this_week_ak_goal"] = ak_divide_by

                if ab_divide_by > 0:
                    ab_percentage = int((float(ret_json["this_week_ab_tally"]) / float(ab_divide_by)) * float(100))
                    if ab_percentage > 100:
                        ab_percentage = 100
                    ret_json["this_week_ab_progress"] = str(ab_percentage) + "%"
                if cd_divide_by > 0:
                    cd_percentage = int((float(ret_json["this_week_cd_tally"]) / float(cd_divide_by)) * float(100))
                    if cd_percentage > 100:
                        cd_percentage = 100
                    ret_json["this_week_cd_progress"] = str(cd_percentage) + "%"

                if ak_divide_by > 0:
                    ak_percentage = int((float(ret_json["this_week_ak_tally"]) / float(ak_divide_by)) * float(100))
                    if ak_percentage > 100:
                        ak_percentage = 100
                    ret_json["this_week_ak_progress"] = str(ak_percentage) + "%"

                lb_stats = LeaderBoardStat.query(
                    ndb.AND(
                        LeaderBoardStat.metric_key == "hours_knocked_v2",
                        LeaderBoardStat.dt >= start_dt,
                        LeaderBoardStat.dt <= end_dt,
                        LeaderBoardStat.office_identifier == parsed_info["office_identifier"]
                    )
                )

                for stat in lb_stats:
                    if stat.rep_id in ret_json["this_week_hks"].keys():
                        ret_json["this_week_hks"][stat.rep_id] += 1
                        
                start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
                while not start_dt.isoweekday() == 7:
                    start_dt = start_dt + timedelta(days=-1)

                start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
                end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
                end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

                start_dt = start_dt + timedelta(days=-7)
                end_dt = end_dt + timedelta(days=-7)

                goals = RepGoal.query(RepGoal.start_date >= start_dt.date())
                for goal in goals:
                    if goal.rep_identifier in rep_identifier_rep_id_dict.keys():
                        rep_id = rep_identifier_rep_id_dict[goal.rep_identifier]
                        if rep_id in ret_json["this_week_ab_goals"].keys():
                            info = json.loads(goal.goal_info)
                            if "AC" in info.keys():
                                ret_json["this_week_ab_goals"][rep_id] = info["AC"]

        ret_json["one_on_one_details"] = Helpers.bubble_sort(ret_json["one_on_one_details"], "dt")
        ret_json["one_on_one_details"].reverse()
        for item in ret_json["one_on_one_details"]:
            item["dt"] = str(item["dt"])

    elif parsed_info["type"] == "LastWeekStatsForRep":
        ret_json = {"hk_goal": 0, "hk_tally": 0, "qc_goal": 0, "qc_tally": 0, "ab_goal": 0, "ab_tally": 0, "ak_goal": 0, "ak_tally": 0, "cd_goal": 0, "cd_tally": 0}
        h_p_t = Helpers.pacific_today()
        if h_p_t.isoweekday() == 6:
            h_p_n = Helpers.pacific_now()
            if h_p_n.hour >= 18:
                h_p_n = h_p_n + timedelta(days=1)
                h_p_t = h_p_n.date()
                
        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        start_dt = start_dt + timedelta(days=-14)
        end_dt = end_dt + timedelta(days=-14)

        goal = RepGoal.first(
            ndb.AND(
                RepGoal.start_date == start_dt.date(),
                RepGoal.rep_identifier == parsed_info["identifier"]
            )
        )
        if not goal is None:
            g_info = json.loads(goal.goal_info)
            if "HK" in g_info.keys():
                ret_json["hk_goal"] = g_info["HK"]
            if "QC" in g_info.keys():
                ret_json["qc_goal"] = g_info["QC"]
            if "AC" in g_info.keys():
                ret_json["ab_goal"] = g_info["AC"]
            if "AK" in g_info.keys():
                ret_json["ak_goal"] = g_info["AK"]
            if "CD" in g_info.keys():
                ret_json["cd_goal"] = g_info["CD"]

        office_cond = (LeaderBoardStat.office_identifier == parsed_info["office_identifier"])
        start_dt = datetime.now()
        end_dt = datetime.now()

        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        start_dt = start_dt + timedelta(days=-7)
        end_dt = end_dt + timedelta(days=-7)

        
        stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key.IN(["hours_knocked_v2", "leads_acquired", "app_stat_NI", "appointments_kept", "packets_submitted"]),
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= end_dt,
                office_cond
            )
        )

        rep = FieldApplicationUser.first(FieldApplicationUser.identifier == parsed_info["identifier"])
        if not rep is None:        
            hk_tally = 0
            cd_tally = 0
            ni_tally = 0
            ab_tally = 0
            ak_tally = 0
            qc_total = 0
            out_of_bounds_qc_total = 0
            net_qcs = 0
            for stat in stats:
                if stat.rep_id == rep.rep_id:
                    cd_tally += int(stat.metric_key == "packets_submitted")
                    ni_tally += int(stat.metric_key == "app_stat_NI")
                    ab_tally += (int(stat.metric_key == "leads_acquired"))
                    hk_tally += (int(stat.metric_key == "hours_knocked_v2"))
                    ak_tally += (int(stat.metric_key == "appointments_kept"))

                    if stat.in_bounds == False:
                        if stat.metric_key == "app_stat_NI":
                            out_of_bounds_qc_total += 1

            qc_total = ab_tally + ni_tally
            net_qcs = qc_total - out_of_bounds_qc_total
            if net_qcs < 0:
                net_qcs = 0
            
            ret_json["hk_tally"] = hk_tally
            ret_json["qc_tally"] = net_qcs
            ret_json["ab_tally"] = ab_tally
            ret_json["ak_tally"] = ak_tally
            ret_json["cd_tally"] = cd_tally

    elif parsed_info["type"] == "QuadrantCountQuery":
        ret_json = {"count": 0}
        quadrants = RepQuadrant.query(
            ndb.AND(
                RepQuadrant.active == True,
                RepQuadrant.rep_identifier == parsed_info["identifier"]
            )
        )

        for quadrant in quadrants:
            ret_json["count"] += 1

    elif parsed_info["type"] == "ProfilePicSave":
        from io import BytesIO
        import base64
        from PIL import Image
        import StringIO
        import cloudstorage as gcs

        img_bytes = BytesIO(base64.b64decode(parsed_info["B64"]))
        img = Image.open(img_bytes)
        if parsed_info["rotate"] == "1":
            img = img.rotate(-90)
            img.load()
        original_width, original_height = img.size
        original_width = int(original_width)
        original_height = int(original_height)
        img1 = img.resize((int(float(original_width) * float("0.8")), int(float(original_height) * float("0.9"))), Image.ANTIALIAS)
        img1.load()

        left = int(parsed_info["crop_box_left"])
        top = int(parsed_info["crop_box_top"])
        right = int(parsed_info["crop_box_right"])
        bottom = int(parsed_info["crop_box_bottom"])
        frame_width = int(parsed_info["image_width"])
        frame_height = int(parsed_info["image_height"])

        new_left = int((float(original_width) * float(left)) / frame_width)
        new_top = int((float(original_height) * float(top)) / frame_height)
        new_right = int((float(original_width) * float(right)) / frame_width)
        new_bottom = int((float(original_height) * float(bottom)) / frame_height)

        img1 = img1.crop(
            (
                new_left,
                new_top,
                new_right,
                new_bottom
            )
        )
        img1.load()

        img1 = img.resize((1000, 1000), Image.ANTIALIAS)
        img1.load()
        output = StringIO.StringIO()
        img1.save(output, format='JPEG')

        output.seek(0)
        output_s = output.read()

        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)

        filename = bucket + '/Images/ProfilePictures/Full/' + parsed_info["identifier"] + '.jpg'
        gcs_file = gcs.open(
                    filename,
                    'w',
                    content_type="image/jpeg",
                    options=
                    {
                        'x-goog-meta-foo': 'foo',
                        'x-goog-meta-bar': 'bar',
                        'x-goog-acl': 'public-read',
                        'cache-control': 'no-cache'
                    },
                    retry_params=write_retry_params
        )
        gcs_file.write(output_s)
        gcs_file.close()
        output.close()

        img1 = img.resize((200, 200), Image.ANTIALIAS)
        img1.load()
        output2 = StringIO.StringIO()
        img1.save(output2, format='JPEG')

        output2.seek(0)
        output_s2 = output2.read()

        filename2 = bucket + '/Images/ProfilePictures/Thumb/' + parsed_info["identifier"] + '.jpg'
        gcs_file2 = gcs.open(
                    filename2,
                    'w',
                    content_type="image/jpeg",
                    options=
                    {
                        'x-goog-meta-foo': 'foo',
                        'x-goog-meta-bar': 'bar',
                        'x-goog-acl': 'public-read',
                        'cache-control': 'no-cache'
                    },
                    retry_params=write_retry_params
        )
        gcs_file2.write(output_s2)
        gcs_file2.close()
        output2.close()


    elif parsed_info["type"] == "Stats":
        ret_json = {}
        start_dt = datetime.now()
        end_dt = datetime.now()
        h_p_t = Helpers.pacific_today()

        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)
        
        this_week_acs = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "leads_acquired",
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= Helpers.pacific_now()
            )
        )

        ac_count = 0
        for ac in this_week_acs:
            if ac.rep_id == parsed_info["rep_id"]:
                ac_count += 1
    
        ret_json["ACs"] = ac_count

        cd_count = 0
        this_week_cds = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "packets_submitted",
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= Helpers.pacific_now()
            )
        )
        for cd in this_week_cds:
            if cd.rep_id == parsed_info["rep_id"]:
                cd_count += 1

        ret_json["CDs"] = cd_count

        hours_knocked_this_week = 0
        this_week_knocks = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "hours_knocked_v2",
                LeaderBoardStat.dt >= start_dt,
                LeaderBoardStat.dt <= Helpers.pacific_now()
            )
        )        
        for knock in this_week_knocks:
            if knock.rep_id == parsed_info["rep_id"]:
                hours_knocked_this_week += 1                        

        ret_json["HKs_this_week"] = hours_knocked_this_week

        month_start = Helpers.pacific_now()
        while not month_start.day == 1:
            month_start = month_start + timedelta(days=-1)

        month_start = datetime(month_start.year, month_start.month, month_start.day, 0, 0, 0)

        hours_knocked_this_month = 0

        this_month_knocks = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "hours_knocked_v2",
                LeaderBoardStat.dt >= month_start,
                LeaderBoardStat.dt <= Helpers.pacific_now()
            )
        )
        for knock in this_month_knocks:
            if knock.rep_id == parsed_info["rep_id"]:
                hours_knocked_this_month += 1

        ret_json["HKs_this_month"] = hours_knocked_this_month

        last_month_start = datetime(month_start.year, month_start.month, month_start.day) + timedelta(days=-1)
        while not last_month_start.day == 1:
            last_month_start = last_month_start + timedelta(days=-1)            
        
        last_month_start = datetime(last_month_start.year, last_month_start.month, last_month_start.day, 0, 0, 0)
        last_month_end = datetime(month_start.year, month_start.month, month_start.day, 0, 0, 0)
        last_month_end = last_month_end + timedelta(seconds=-1)

        last_week_start = start_dt + timedelta(days=-7)
        last_week_end = last_week_start + timedelta(days=7)
        last_week_end = last_week_end + timedelta(seconds=-1)

        hours_knocked_last_week = 0
        
        last_week_knocks = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "hours_knocked_v2",
                LeaderBoardStat.dt >= last_week_start,
                LeaderBoardStat.dt <= last_week_end
            )
        )
        for knock in last_week_knocks:
            if knock.rep_id == parsed_info["rep_id"]:
                hours_knocked_last_week += 1

        ret_json["HKs_last_week"] = hours_knocked_last_week

        hours_knocked_last_month = 0

        last_month_knocks = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "hours_knocked_v2",
                LeaderBoardStat.dt >= last_month_start,
                LeaderBoardStat.dt <= last_month_end
            )
        )

        for knock in last_month_knocks:
            if knock.rep_id == parsed_info["rep_id"]:
                hours_knocked_last_month += 1

        ret_json["HKs_last_month"] = hours_knocked_last_month

        h_p_t = Helpers.pacific_today()
        if h_p_t.isoweekday() == 6:
            h_p_n = Helpers.pacific_now()
            if h_p_n.hour >= 18:
                h_p_n = h_p_n + timedelta(days=1)
                h_p_t = h_p_n.date()
                
        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            start_dt = start_dt + timedelta(days=-1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        start_dt = start_dt + timedelta(days=-7)
        end_dt = end_dt + timedelta(days=-7)

        goal = RepGoal.first(
            ndb.AND(
                RepGoal.start_date >= start_dt.date(),
                RepGoal.rep_identifier == parsed_info["identifier"]
            )
        )
        if goal is None:
            ret_json["AC_goals"] = 0
            ret_json["CD_goals"] = 0
        else:
            info = json.loads(goal.goal_info)
            ret_json["AC_goals"] = info["AC"]
            ret_json["CD_goals"] = info["CD"]
        
        ret_json["ac_percentage"] = 100.0
        ret_json["cd_percentage"] = 100.0

        if ret_json["AC_goals"] > 0:
            ret_json["ac_percentage"] = round((float(ret_json["ACs"]) / float(ret_json["AC_goals"])), 2) * float(100)

        if ret_json["CD_goals"] > 0:
            ret_json["cd_percentage"] = round((float(ret_json["CDs"]) / float(ret_json["CD_goals"])), 2) * float(100)        
        
        if ret_json["ac_percentage"] > 100.0:
            ret_json["ac_percentage"] = 100.0
        if ret_json["cd_percentage"] > 100.0:
            ret_json["cd_percentage"] = 100.0

        r_ids_to_query = ["-1"]
        lb_data = {}
        for stat in this_week_acs:
            if not stat.rep_id in lb_data.keys():
                lb_data[stat.rep_id] = 0
            lb_data[stat.rep_id] += 1
            r_ids_to_query.append(stat.rep_id)
        
        rep_id_to_name = {}
        rep_id_to_identifier = {}
        reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(r_ids_to_query))
        for rep in reps:
            rep_id_to_name[rep.rep_id] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
            rep_id_to_identifier[rep.rep_id] = rep.identifier
        
        winner_data = {}
        winner_data["spot_1_name"] = "Nobody";
        winner_data["spot_1_tally"] = -1;
        winner_data["spot_1_identifier"] = "-1";
        winner_data["spot_2_name"] = "Nobody";
        winner_data["spot_2_tally"] = -1;
        winner_data["spot_2_identifier"] = "-1";
        winner_data["spot_3_name"] = "Nobody";
        winner_data["spot_3_tally"] = -1;
        winner_data["spot_3_identifier"] = "-1";
        winner_data["spot_4_name"] = "Nobody";
        winner_data["spot_4_tally"] = -1;
        winner_data["spot_4_identifier"] = "-1";
        winner_data["spot_5_name"] = "Nobody";
        winner_data["spot_5_tally"] = -1;
        winner_data["spot_5_identifier"] = "-1";

        winning_rep_ids = []
        lb_data_cpy = []
        for item in lb_data.keys():
            lb_data_cpy.append({"rep_id": item, "tally": lb_data[item]})

        lb_data_cpy = Helpers.bubble_sort(lb_data_cpy, "tally")
        lb_data_cpy.reverse()
        cnt = 0
        while cnt < 5:
            if len(lb_data_cpy) >= cnt + 1:
                item = lb_data_cpy[cnt];
                idx = cnt + 1;
                idx = str(idx);
                winner_data["spot_" + idx + "_name"] = rep_id_to_name[item["rep_id"]];
                winner_data["spot_" + idx + "_tally"] = item["tally"]
                winner_data["spot_" + idx + "_identifier"] = rep_id_to_identifier[item["rep_id"]];
            cnt += 1

        cnt = 1
        while cnt < 6:
            if winner_data["spot_" + str(cnt) + "_tally"] == -1:
                winner_data["spot_" + str(cnt) + "_tally"] = 0
            cnt += 1

        for item in winner_data.keys():
            ret_json[item] = winner_data[item]

    locs = locals()
    keys = locs.keys()
    if "ret_json" in keys:
        self.response.out.write(json.dumps(ret_json))
