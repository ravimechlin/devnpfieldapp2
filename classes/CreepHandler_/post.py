def post(self):
    self.response.content_type = "application/json"
    latest_post = {}
    note = CustomerNote.query(CustomerNote.note_key == "sales_form_post").order(-CustomerNote.inserted_utc).fetch(1, offset=0)
    for n in note:
        app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == n.field_app_identifier)
        if not app_entry is None:
            rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
            if not rep is None:
                millis_since_epoch = int((n.inserted_utc - datetime(1970, 1, 1)).total_seconds() * 1000)
                latest_post["exists"] = True
                latest_post["utc"] = millis_since_epoch
                latest_post["street"] = app_entry.customer_address
                latest_post["address"] = app_entry.customer_address
                latest_post["city"] = app_entry.customer_city
                latest_post["state"] = app_entry.customer_state
                latest_post["postal"] = app_entry.customer_postal
                latest_post["rep_name"] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
                latest_post["identifier"] = app_entry.identifier
                latest_post["rep_identifier"] = rep.identifier

    if "identifier" in latest_post.keys():
        if str(self.request.get("identifier")) == latest_post["identifier"]:
            latest_post = {"exists": False}
                

    self.response.out.write(json.dumps(latest_post))
