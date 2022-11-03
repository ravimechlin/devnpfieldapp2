def post(self):
    from google.appengine.api import app_identity
    fromm = str(self.request.get("From")).split("+")[1]
    if len(fromm) == 11:
        fromm = fromm[1:]
    to = str(self.request.get("To"))
    if len(to) == 11:
        to = to[1:]
    elif len(to) == 12:
        to = to[2:]

    to = to.replace("+", "")
    body = unicode(self.request.get("Body"))
    img = str(self.request.get("MediaUrl0"))
    m_url = "-1"
    if len(img) > 4:
        m_url = img

    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.customer_phone == fromm)
    if not app_entry is None:
        rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
        if not rep is None:
            comm = CustomerComm(
                identifier=Helpers.guid(),
                media_url=m_url,
                dt=Helpers.pacific_now(),
                rep_identifier=rep.identifier,
                field_app_identifier=app_entry.identifier,
                sender=app_entry.identifier,
                msg=body
            )
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

            url = "https://" + app_identity.get_application_id() + ".appspot.com/comm/" + app_entry.identifier + "?guid=" + Helpers.guid()
            msg = "From " + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + ": " + body + ". DON'T text back, reply here: " + url
            Helpers.send_sms(rep.rep_phone, msg)



