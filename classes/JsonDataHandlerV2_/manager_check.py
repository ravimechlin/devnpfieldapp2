def manager_check(self):
    self.response.content_type = "application/json"
    ret_json = {"success": False}
    user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not user is None:
        ret_json["success"] = user.is_manager or user.user_type == "solar_pro_manager"
    self.response.out.write(json.dumps(ret_json))
