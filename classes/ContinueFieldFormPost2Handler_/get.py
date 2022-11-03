def get(self):
    keyy = "allow_CPF_work_for_" + self.request.get("e_identifier")
    val = memcache.get(keyy)

    if val == "true":
        ents = FieldApplicationEntry.query(FieldApplicationEntry.identifier == self.request.get("e_identifier"))
        for ent in ents:
            proposal_id = Helpers.create_CPF_customer_proposal2(ent)

            template_values = {}
            template_values["app_entry_identifier"] = self.request.get("e_identifier")
            template_values["booking_identifier"] = self.request.get("b_identifier")
            template_values["proposal_identifier"] = proposal_id
            template_values["location"] = "continue3"

            path = Helpers.get_html_path('client_side_redirect.html')
            self.response.out.write(template.render(path, template_values))

