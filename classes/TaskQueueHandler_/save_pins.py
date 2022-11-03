def save_pins(self):
    import MySQLdb

    points = json.loads(self.request.get("all_points"))
        
    db = Helpers.connect_to_cloud_sql()
    cursor = db.cursor()
    cursor.execute("USE addresses;")
    sql = "SELECT ST_AsText(coordinates) FROM points WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(("
    for point in (points + [points[0]]):
        p = point.split(",")
        sql += (p[0].strip() + " " + p[1].strip() + ", ")
    sql = sql[0:len(sql) - 2]
    sql += "))'), points.coordinates);"
    cursor.execute(sql)

    points_to_save = []
    for row in cursor.fetchall():
        pt_str = row[0]
        pt_str_vals = pt_str.split(" ")
        lat = pt_str_vals[0].replace("POINT(", "")
        lng = pt_str_vals[1].replace(")", "")
        PPoint = PinPoint(
            identifier=Helpers.guid(),                    
            quadrant_identifier=self.request.get("quadrant_identifier"),
            rep_identifier=self.request.get("rep_identifier"),
            longitude=float(lng),
            latitude=float(lat),
            status=2,
            extra_info="{}",
            created=Helpers.pacific_now(),
            modified=Helpers.pacific_now(),
            manager_identifier=self.request.get("manager_identifier")
        )
        points_to_save.append(PPoint)

    cursor.close()
    db.close()
    if len(points_to_save) == 1:
        points_to_save[0].put()
    if len(points_to_save) > 1:
        ndb.put_multi(points_to_save)
