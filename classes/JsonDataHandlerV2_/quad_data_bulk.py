def quad_data_bulk(self):
    self.response.content_type = "application/json"
    ret_json = {"quads": []}
    
    quadrant_identifier_idx_dict = {}
    kv_keys_to_query = ["-1"]
    quadrants = RepQuadrant.query()
    for quadrant in quadrants:
        quadrant_identifier_idx_dict[quadrant.identifier] = len(ret_json["quads"])
        obj = {"identifier": quadrant.identifier}
        obj["active"] = quadrant.active
        obj["all_points"] = quadrant.all_points
        obj["rep_identifier"] = quadrant.rep_identifier
        obj["manager_identifier"] = quadrant.manager_identifier
        obj["office_identifier"] = quadrant.office_identifier
        obj["time_assigned"] = "1970-01-01"
        obj["notes"] = ""
        ret_json["quads"].append(obj)

    details = QuadrantAssignmentDetails.query()
    for detail in details:
        idx = quadrant_identifier_idx_dict[detail.quadrant_identifier]
        ret_json["quads"][idx]["time_assigned"] = str(detail.dt.date())
    
    self.response.out.write(json.dumps(ret_json))
