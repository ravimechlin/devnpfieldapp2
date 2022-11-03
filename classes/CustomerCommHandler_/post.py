def post(self, identifier):
    from google.appengine.api import search

    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == identifier)
    if not app_entry is None:
        rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
        if not rep is None:
            comm = CustomerComm(
                identifier=Helpers.guid(),
                media_url="-1",
                dt=Helpers.pacific_now(),
                rep_identifier=rep.identifier,
                field_app_identifier=identifier,
                sender=rep.identifier,
                msg=self.request.get("msg")
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

            Helpers.send_sms(app_entry.customer_phone, comm.msg, "+19513862382", None)
