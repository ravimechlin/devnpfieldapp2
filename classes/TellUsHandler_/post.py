def post(self, identifier):
    user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not user is None:
        week_dt_vals = self.request.get("week_dt").split("-")
        week_date = date(int(week_dt_vals[0]), int(week_dt_vals[1]), int(week_dt_vals[2]))

        existing_response = WeeklySurvey.first(
            ndb.AND(
                WeeklySurvey.rep_identifier == user.identifier,
                WeeklySurvey.week_dt == week_date
            )
        )
        if existing_response is None:
            to_save = WeeklySurvey(
                identifier=Helpers.guid(),
                rep_identifier=user.identifier,
                response=self.request.get("data"),
                submitted=Helpers.pacific_now(),
                week_dt=week_date,
                user_type=self.request.get("user_type"),
                office_identifier=user.main_office
            )
            to_save.put()




