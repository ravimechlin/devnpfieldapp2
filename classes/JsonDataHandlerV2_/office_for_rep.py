def office_for_rep(self):
    self.response.content_type = "application/json"
    ret_json = {"identifier": "-1"}
    rep = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not rep is None:
        ret_json["identifier"] = rep.main_office
    self.response.out.write(json.dumps(ret_json))
