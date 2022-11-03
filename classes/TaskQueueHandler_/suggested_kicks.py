def suggested_kicks(self):
    from google.appengine.api import app_identity
    from datetime import datetime
    from datetime import timedelta
    users = FieldApplicationUser.query(ndb.AND(
        FieldApplicationUser.current_status == 0,
        FieldApplicationUser.user_type.IN(["solar_pro", "solar_pro_manager"])
    ))

    rep_id_rep_name_dict = {}
    rep_identifier_rep_name_dict = {}
    rep_id_rep_identifier_dict = {}
    rep_identifier_rep_id_dict = {}
    rep_identifier_email_dict = {}
    rep_identifier_registration_dict = {}
    kv_keys_to_query = ["-1"]
    all_rep_ids = []
    for user in users:
        kv_keys_to_query.append("kick_halt_" + user.identifier)
        rep_id_rep_name_dict[user.rep_id] = user.first_name.strip().title() + " " + user.last_name.strip().title()
        rep_identifier_rep_name_dict[user.identifier] = user.first_name.strip().title() + " " + user.last_name.strip().title()
        rep_id_rep_identifier_dict[user.rep_id] = user.identifier
        rep_identifier_rep_id_dict[user.identifier] = user.rep_id
        rep_identifier_email_dict[user.identifier] = user.rep_email
        rep_identifier_registration_dict[user.identifier] = datetime(user.registration_date.year, user.registration_date.month, user.registration_date.day)
        all_rep_ids.append(user.rep_id)

    now = Helpers.pacific_now()
    six_days_ago = now + timedelta(days=-6)
    six_days_ago = datetime(six_days_ago.year, six_days_ago.month, six_days_ago.day)

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.dt >= six_days_ago,
            LeaderBoardStat.metric_key == "hours_knocked_v2"
        )
    )

    found_rep_ids = []
    for stat in stats:
        if not stat.rep_id in found_rep_ids:
            found_rep_ids.append(stat.rep_id)


    already_suggested = []
    existing_kick_suggestions = SuggestedKick.query()
    for kick in existing_kick_suggestions:
        already_suggested.append(kick.rep_identifier)

    halted_identifiers = []
    kvs = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(kv_keys_to_query))
    for kv in kvs:
        rep_identifier = kv.keyy.replace("kick_halt_", "")
        halted_identifiers.append(rep_identifier)


    eight_days_ago = Helpers.pacific_now() + timedelta(days=-8)
    eight_days_ago = datetime(eight_days_ago.year, eight_days_ago.month, eight_days_ago.day)
    kicks_to_put = []
    for rep_id in all_rep_ids:
        if not rep_id in found_rep_ids:
            r_identifier = rep_id_rep_identifier_dict[rep_id]
            if not r_identifier in already_suggested:
                if not r_identifier in halted_identifiers:
                    registration_date = rep_identifier_registration_dict[r_identifier]
                    if registration_date < eight_days_ago:                    
                        kick = SuggestedKick(
                            identifier=Helpers.guid(),
                            rep_identifier=r_identifier,
                            suggested_kick_dt=(now + timedelta(days=4)).date()
                        )
                        kicks_to_put.append(kick)

                    msg = "New Power has noticed you have not produced any HKs over the last 5 business days.  If you are NOT quitting, please follow the link in this email and click the 'No, I am not quitting' button and let us know when you will be back to work.  If you do not respond within 72 hours, your account will be deactivated.\r\n\r\nhttps://" + app_identity.get_application_id() + ".appspot.com/bootstrap/html/contest_deactivation.html?identifier=" + r_identifier
                    Helpers.send_email(rep_identifier_email_dict[r_identifier], "Are you quitting? Action required", msg)

    if len(kicks_to_put) == 1:
        kicks_to_put[0].put()
    elif len(kicks_to_put) > 1:
        ndb.put_multi(kicks_to_put)

