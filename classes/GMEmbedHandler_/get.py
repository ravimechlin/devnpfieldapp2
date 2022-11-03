def get(self, address, width, height):
    template_dict = {}
    template_dict["width"] = width
    template_dict["height"] = height
    template_dict["address"] = address

    path = Helpers.get_html_path('gm_embed.html')
    self.response.out.write(template.render(path, template_dict))

