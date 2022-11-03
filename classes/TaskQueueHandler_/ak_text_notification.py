def ak_text_notification(self):
    now = Helpers.pacific_now()
    if now.hour >= 23:
        return
    if now.hour < 8:
        return

    from google.appengine.api import urlfetch
    from google.appengine.api import app_identity
    
    types = ["energy_expert", "sales_manager"]
    users = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.user_type.IN(types),
            FieldApplicationUser.current_status == 0
        )
    )

    for user in users:
        try:
            req = urlfetch.fetch(
                url="https://" + app_identity.get_application_id() + ".appspot.com/data?fn=sp2_annoy&identifier=" + user.identifier + "&tres=1",
                method=urlfetch.GET,
                deadline=30
            )
            jaysawn = json.loads(req.content)
            if jaysawn["has_item"]:
                #Helpers.send_sms(user.rep_phone, "Action needed! Please respond here: https://" + app_identity.get_application_id() + ".appspot.com/AKR/" + user.identifier)
                x = 66
        except:
            x = 5
    
