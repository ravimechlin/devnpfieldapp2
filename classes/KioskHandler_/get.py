def get(self, speed):
    template_items = {}
    path = Helpers.get_html_path('kiosk.html')
    self.response.out.write(template.render(path, template_items))

