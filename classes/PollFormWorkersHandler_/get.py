def get(self):
    template_values = {}
    template_values["token"] = self.request.get("tk_identifier")
    template_values["booking_identifier"] = self.request.get("b_identifier")
    template_values["field_application_entry_identifier"] = self.request.get("e_identifier")
    template_values["app_entry_identifier"] = self.request.get("e_identifier")

    path = Helpers.get_html_path('poll_form_workers.html')
    self.response.out.write(template.render(path, template_values))
