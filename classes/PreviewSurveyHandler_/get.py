def get(self):
    template_values = {}
    template_values["survey_identifier"] = self.request.get("identifier")

    if str(self.request.get("b_identifier")) == "" or str(self.request.get("b_identifier")).lower() == "none":
        template_values["has_booking"] = "false"
    else:
        template_values["booking_identifier"] = self.request.get("b_identifier")
        template_values["has_booking"] = "true"
        path = Helpers.get_html_path('preview_survey.html')
        self.response.out.write(template.render(path, template_values))

    path
