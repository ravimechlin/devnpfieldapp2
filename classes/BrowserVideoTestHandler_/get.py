def get(self):
    template_items = {}
    path = Helpers.get_html_path('record_video_test.html')
    self.response.out.write(template.render(path, template_items))
