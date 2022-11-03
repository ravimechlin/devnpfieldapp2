def bounds_update(self):
    import MySQLdb
    now = Helpers.pacific_now()

    quadrant = RepQuadrant.first(RepQuadrant.identifier == self.request.get("identifier"))
    if not quadrant is None:
        existing_pins = PinPoint.query(PinPoint.quadrant_identifier == quadrant.identifier)
        existing_geo_hashes = []
        existing_geo_hash_pin_dict = {}
        for ep in existing_pins:
            existing_geo_hashes.append(str(ep.latitude) + "," + str(ep.longitude))
            existing_geo_hash_pin_dict[str(ep.latitude) + "," + str(ep.longitude)] = ep

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

        new_geo_hashes = []
        pins_to_save = []
        for row in cursor.fetchall():
            pt_str = row[0]
            pt_str_vals = pt_str.split(" ")
            lat = pt_str_vals[0].replace("POINT(", "")
            lng = pt_str_vals[1].replace(")", "")
            new_geo_hashes.append(str(float(lat)) + "," + str(float(lng)))

            point = PinPoint(
                identifier=Helpers.guid(),                    
                quadrant_identifier=quadrant.identifier,
                rep_identifier=quadrant.rep_identifier,
                longitude=float(lng),
                latitude=float(lat),
                status=2,
                extra_info="{}",
                created=now,
                modified=now,
                manager_identifier=quadrant.manager_identifier
            )
            last_hash = new_geo_hashes[len(new_geo_hashes) - 1]
            if not last_hash in existing_geo_hashes:
                pins_to_save.append(point)

        cursor.close()
        db.close()

        pin_to_delete = None
        keys_to_delete = []
        for key in existing_geo_hashes:
            if not key in new_geo_hashes:
                keys_to_delete.append(existing_geo_hash_pin_dict[key].key)
                pin_to_delete = existing_geo_hash_pin_dict[key]

        if len(keys_to_delete) == 1:
            pin_to_delete.key.delete()
        elif len(keys_to_delete) > 1:
            ndb.delete_multi(keys_to_delete)

        if len(pins_to_save) == 1:
            pins_to_save[0].put()
        elif len(pins_to_save) > 1:
            ndb.put_multi(pins_to_save)
