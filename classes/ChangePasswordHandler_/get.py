def get(self):
    path = Helpers.get_html_path('changepassword.html')
    template_values = {}
    self.response.out.write(template.render(path, template_values))

