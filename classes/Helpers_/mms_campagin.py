@staticmethod
def mms_campaign(campaign_key, app_entry, rep):
    from google.appengine.api import app_identity
    from google.appengine.api import search
    from google.appengine.api import memcache

    val = memcache.get(campaign_key + "_" + app_entry.identifier)
    if val is None:
        memcache.set(key=campaign_key + "_" + app_entry.identifier, value="1", time=60 * 120)
        comm = CustomerComm()
        comm.identifier = Helpers.guid()
        msg = ""
        media_url = None
        if campaign_key in ["introductory_selfie", "introductory_selfie_own"]:
            weekday_map = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
            msg = "See you " + weekday_map[app_entry.sp_two_time.isoweekday()] + " at " + app_entry.sp_two_time.strftime("%I:%M %p")
            media_url = None
            if Helpers.gcs_file_exists("/MarketingCollateral/" + campaign_key + "/" + rep.identifier + "/video.3gp"):
                media_url = "https://storage.googleapis.com/" + app_identity.get_application_id() + ".appspot.com/MarketingCollateral/" + campaign_key + "/" + rep.identifier + "/video.3gp"
            elif Helpers.gcs_file_exists("/MarketingCollateral/introductory_selfie/fallback.3gp"):
                media_url = "https://storage.googleapis.com/" + app_identity.get_application_id() + ".appspot.com/MarketingCollateral/" + campaign_key + "/fallback.3gp"

            try:
                Helpers.send_sms(app_entry.customer_phone, msg, "+19513862382", media_url)
            except:
                media_url = media_url

        m_url = "-1"
        if media_url is not None:
            m_url = media_url
        comm.media_url = m_url
        comm.dt = Helpers.pacific_now()
        comm.rep_identifier = rep.identifier
        comm.field_app_identifier = app_entry.identifier
        comm.sender = rep.identifier
        comm.msg = msg
        comm.put()

        index = search.Index(name="cust_comm")
        doc = search.Document(
            fields=[
                search.TextField(name="identifier", value=comm.identifier),
                search.TextField(name="sender", value=comm.sender),
                search.TextField(name="rep", value=comm.rep_identifier),
                search.TextField(name="field_app_identifier", value=comm.field_app_identifier),
                search.TextField(name="name", value=app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()),
                search.TextField(name="rep_name", value=rep.first_name.strip().title() + " " + rep.last_name.strip().title()),
                search.TextField(name="msg", value=comm.msg),
                search.DateField(name="dt", value=comm.dt)
            ]
        )
        index.put(doc)
