def get(self):
    from google.appengine.api import app_identity
    path = Helpers.get_html_path("ios_install.html")
    template_values = {}
    template_values["app_id"] = app_identity.get_application_id()
    self.response.out.write(template.render(path, template_values))

