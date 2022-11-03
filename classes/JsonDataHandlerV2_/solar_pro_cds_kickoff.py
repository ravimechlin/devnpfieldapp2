def solar_pro_cds_kickoff(self):
    from google.appengine.api import taskqueue
    taskqueue.add(url="/tq/solar_pro_cds", params={"start_dt": self.request.get("start_dt"), "end_dt": self.request.get("end_dt"), "email": self.request.get("email")})
#
#
