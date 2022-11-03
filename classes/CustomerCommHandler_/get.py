def get(self, identifier):
    template_values = {}
    template_values["identifier"] = identifier
    path = Helpers.get_html_path('comm.html')
    self.response.out.write(template.render(path, template_values))
