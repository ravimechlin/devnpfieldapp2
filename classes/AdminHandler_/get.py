def get(self): 
    template_values = {}
    path = Helpers.get_html_path('admin.html')
    #if self.request.cookies.get('secret') == 'shh':
    self.response.out.write(template.render(path, template_values))
    #else:
        #self.response.out.write(".")

