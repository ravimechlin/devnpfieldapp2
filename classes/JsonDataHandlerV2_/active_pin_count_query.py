def active_pin_count_query(self):
    self.response.content_type = "application/json"
    ret_json = {"pins": -1}
    user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not user is None:
        quads = RepQuadrant.query(
            ndb.AND(
                RepQuadrant.active == True,
                RepQuadrant.rep_identifier == user.identifier
            )
        )
        quad_ids = ["-1"]
        for quad in quads:
            quad_ids.append(quad.identifier)

        ret_json["pins"] = PinPoint.query(PinPoint.quadrant_identifier.IN(quad_ids)).count()

    self.response.out.write(json.dumps(ret_json))
