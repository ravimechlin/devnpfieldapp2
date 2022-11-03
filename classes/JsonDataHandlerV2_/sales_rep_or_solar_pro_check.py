def sales_rep_or_solar_pro_check(self):
    self.response.content_type = "application/json"
    ret_json = {"success": True}
    rep = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not rep is None:
        if rep.user_type == "super":
            ret_json["success"] = (not rep.user_type == "super")
    self.response.out.write(json.dumps(ret_json))
