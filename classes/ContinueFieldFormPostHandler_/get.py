def get(self):
    keyy = "allow_CPF_work_for_" + self.request.get("e_identifier")
    val = memcache.get(keyy)

    if val == "true":
        ents = FieldApplicationEntry.query(FieldApplicationEntry.identifier == self.request.get("e_identifier"))
        for ent in ents:
            Helpers.create_CPF_customer_proposal(ent)

            template_values = {}
            template_values["app_entry_identifier"] = self.request.get("e_identifier")
            template_values["booking_identifier"] = self.request.get("b_identifier")
            template_values["location"] = "continue2"

            path = Helpers.get_html_path('client_side_redirect.html')
            self.response.out.write(template.render(path, template_values))
            #self.redirect("/success?e_identifier=" + self.request.get("e_identifier") + "&b_identifier=" + self.request.get("b_identifier"))

