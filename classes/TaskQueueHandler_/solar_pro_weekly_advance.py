def solar_pro_weekly_advance(self):
    from google.appengine.api import app_identity
    from google.appengine.api import urlfetch
    from datetime import datetime
    from datetime import timedelta

    this_friday = Helpers.pacific_now()
    while not (this_friday.isoweekday() == 5):
        this_friday = this_friday + timedelta(days=1)

    solar_pros = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.user_type.IN(["solar_pro", "solar_pro_manager"]),
            FieldApplicationUser.current_status == 0
        )
    )

    rep_id_rep_identifier_dict = {}
    for solar_pro in solar_pros:
        rep_id_rep_identifier_dict[solar_pro.rep_id] = solar_pro.identifier

    resp = urlfetch.fetch(url="https://" + app_identity.get_application_id() + ".appspot.com/data?fn=get_leaderboard_data&achievement_metric=hours_knocked_v2&time_metric=last_week&office=-1&start=undefined&end=undefined",
                deadline=30,
                method=urlfetch.GET)
    data = json.loads(resp.content)
    rep_ids = data["data"].keys()
    for r_id in rep_ids:
        if data["data"][r_id] >= 20:
            if r_id in rep_id_rep_identifier_dict.keys():
                payout_url = "https://" + app_identity.get_application_id() + ".appspot.com/data?fn=create_v2_transaction"
                payout_url += "&amount=250.00"
                payout_url += "&trans_type=advance"
                payout_url += "&description=Guarantee%20for%20" + data["start_dt"] + "%20---%20" + data["end_dt"] + "."
                payout_url += "&date=" + str(this_friday.date())
                payout_url += "&recipient=" + rep_id_rep_identifier_dict[r_id]
                resp2 = urlfetch.fetch(url=payout_url,
                            deadline=30,
                            method=urlfetch.GET)


    
