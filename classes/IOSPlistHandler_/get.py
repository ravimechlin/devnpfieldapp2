def get(self):
    from google.appengine.api import app_identity
    self.response.content_type = "application/xml"
    path = Helpers.get_html_path("ios_plist.plist")
    template_values = {}
    template_values["app_version"] = Helpers.get_app_version()
    template_values["app_id"] = app_identity.get_application_id()
    self.response.out.write(template.render(path, template_values))

