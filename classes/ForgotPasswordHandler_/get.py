def get(self):
    path = Helpers.get_html_path('forgotpassword.html')
    template_values = {}
    self.response.out.write(template.render(path, template_values))
