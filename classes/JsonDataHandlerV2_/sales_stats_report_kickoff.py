def sales_stats_report_kickoff(self):
    from google.appengine.api import taskqueue
    taskqueue.add(url="/tq/sales_stats_report", params={"start_dt": self.request.get("start_dt"), "end_dt": self.request.get("end_dt"), "email": self.request.get("email")})

