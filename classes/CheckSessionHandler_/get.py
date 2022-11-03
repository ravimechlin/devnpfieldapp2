def get(self):
    self.response.content_type = "application/json"
    ret_json = {}
    ret_json["good"] = True
    self.session = get_current_session()
    try:
        u_id = self.session["user_identifier"]
    except:
        ret_json["good"] = False

    self.response.out.write(json.dumps(ret_json))


