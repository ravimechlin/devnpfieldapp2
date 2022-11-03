def get(self):
    template_values = {}
    path = Helpers.get_html_path('local_storage_test.html')
    self.response.out.write(template.render(path, template_values))
