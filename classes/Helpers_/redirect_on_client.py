@staticmethod
def redirect_on_client(resp, url, timeout, template_file="client_side_redirect_v2.html"):
    template_values = {}
    template_values["timeout"] = str(timeout)
    template_values["redirect_url"] = url
    resp.out.write(template.render(Helpers.get_html_path(template_file), template_values))
