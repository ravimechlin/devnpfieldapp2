def get(self, app_entry_identifier, closer_identifier):
    template_values = {}
    template_values["app_entry_identifier"] = app_entry_identifier
    template_values["closer_identifier"] = closer_identifier
    path = Helpers.get_html_path('appt_confirmation.html')
    self.response.out.write(template.render(path, template_values))
