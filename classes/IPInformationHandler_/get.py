def get(self):
    self.response.content_type = "application/json"
    self.response.out.write(json.dumps(Helpers.ip_geolocation_info(self.request.remote_addr)))
