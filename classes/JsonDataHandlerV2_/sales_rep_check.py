def sales_rep_check(self):
    self.response.content_type = "application/json"
    ret_json = {"success": False}
    rep = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not rep is None:
        ret_json["success"] = (rep.user_type in ["field", "asst_mgr", "co_mgr", "sales_dist_mgr", "rg_mgr", "sales_manager", "energy_expert"])
    self.response.out.write(json.dumps(ret_json))
