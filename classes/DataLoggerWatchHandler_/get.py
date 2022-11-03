def get(self):
    template_values = {}
    template_values["app_bucket"] = app_identity.get_default_gcs_bucket_name()    
    path = Helpers.get_html_path('dl_watch.html')
    self.response.out.write(template.render(path, template_values))

