def get(self, identifier):
    customers = []
    from google.appengine.api import app_identity
    from google.appengine.api import urlfetch
    template_values = {}

    if len(identifier) == 128:    
        template_values["user_identifier"] = identifier
        template_values["single_mode"] = "0"
        template_values["already_found"] = "0"
        req = urlfetch.fetch(
            url="https://" + app_identity.get_application_id() + ".appspot.com/data?fn=sp2_annoy&identifier=" + identifier + "&tres=1",
            method=urlfetch.GET,
            deadline=30
        )
        jaysawn = json.loads(req.content)
        if jaysawn["has_item"]:
            ident = jaysawn["item"]["identifier"]
            obj = {}
            app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == ident)
            if not app_entry is None:
                obj["name"] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
                obj["address"] = app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal
                obj["phone"] = app_entry.customer_phone
                obj["phone_formatted"] = Helpers.format_phone_number(app_entry.customer_phone)
                obj["identifier"] = app_entry.identifier
                customers.append(obj)
    else:
        u_id = identifier.split("_")[0]
        fa_id = identifier.split("_")[1]
        template_values["user_identifier"] = u_id
        template_values["single_mode"] = "1"

        obj = {}
        app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == fa_id)
        if not app_entry is None:
            obj["name"] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
            obj["address"] = app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal
            obj["phone"] = app_entry.customer_phone
            obj["phone_formatted"] = Helpers.format_phone_number(app_entry.customer_phone)
            obj["identifier"] = app_entry.identifier

            customers.append(obj)

        stat = LeaderBoardStat.first(
            ndb.AND(
                LeaderBoardStat.field_app_identifier == fa_id,
                LeaderBoardStat.metric_key == "appointments_kept"
            )
        )
        if not stat is None:
            template_values["already_found"] = "1"

            path = Helpers.get_html_path('ak_already_found.html')
            self.response.out.write(template.render(path, template_values))
            return

    template_values["customers"] = json.dumps(customers)
    path = Helpers.get_html_path('street_view.html')
    self.response.out.write(template.render(path, template_values))

    
    

    

    
