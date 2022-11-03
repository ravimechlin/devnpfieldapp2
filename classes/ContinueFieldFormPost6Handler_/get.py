def get(self):
    keyy = "allow_CPF_work_for_" + self.request.get("e_identifier")
    val = memcache.get(keyy)

    if val == "true":
        ents = FieldApplicationEntry.query(FieldApplicationEntry.identifier == self.request.get("e_identifier"))
        for ent in ents:
            f_name = ent.customer_first_name
            l_name = ent.customer_last_name

            form_fields = {}
            form_fields["first_name"] = f_name
            form_fields["last_name"] = l_name

            urlfetch.fetch(
                url=Helpers.get_apps_script_docusign_forwarder_url(),
                method=urlfetch.POST,
                payload=urllib.urlencode(form_fields),
                deadline=30,
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            )

            self.redirect("/success2?e_identifier=" + self.request.get("e_identifier") + "&b_identifier=" + self.request.get("b_identifier"))

