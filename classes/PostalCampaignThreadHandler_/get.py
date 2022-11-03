def get(self, phone, rep_identifier):
    if phone == "7148767934":
        if rep_identifier == "41738e1361421e6441dae232a634c3b700b4f660b37daa2710af2d26c12e21fa7fe98010153f66d4a1d04c0fd444752ffe93f16122d29fd0318e98ed0ddd968c":
            html = "<html><title>Dropped the ball?</title><body style='padding: 50px'><center><a href='https://www.youtube.com/watch?v=2gzt6GeNLBk&t=0m56s'>Reply to customer</a></center></body></html>"
            self.response.content_type = "text/html"
            self.response.out.write(html)
            return
    
    template_items = {}
    template_items["phone"] = phone
    template_items["rep_identifier"] = rep_identifier
    path = Helpers.get_html_path('postal_campaign.html')
    self.response.out.write(template.render(path, template_items))
