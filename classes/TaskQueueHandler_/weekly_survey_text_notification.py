def weekly_survey_text_notification(self):
    good = False
    now = Helpers.pacific_now()
    if now.isoweekday() == 1:
        if now.hour > 9 and now.hour < 19:
            good = True

    if not good:
        return

    from google.appengine.api import app_identity
    types = ["energy_expert", "sales_manager", "solar_pro_manager"]
    users = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.user_type.IN(types),
            FieldApplicationUser.current_status == 0
        )
    )

    for user in users:
        try:
            req = urlfetch.fetch(
                url="https://" + app_identity.get_application_id() + ".appspot.com/data?fn=survey_response_check&identifier=" + user.identifier,
                method=urlfetch.GET,
                deadline=30
            )
            jaysawn = json.loads(req.content)
            if not jaysawn["found"]:
                Helpers.send_sms(user.rep_phone, "Action needed! We need your weekly report. Fill out the form here: https://" + app_identity.get_application_id() + ".appspot.com/tell_us/" + user.identifier)
        except:
            x = 5
