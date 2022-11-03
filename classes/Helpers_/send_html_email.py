@staticmethod
def send_html_email(to, subject, template_name, template_vars):
    apps_script_mailer_url = Helpers.get_apps_script_mailer_url()

    form_fields = {"to": to, "subject": subject, "template": template_name, "template_vars": json.dumps(template_vars)}

    form_data = urllib.urlencode(form_fields)

    resp = urlfetch.fetch(
                            url=apps_script_mailer_url,
                            payload=form_data,
                            deadline=30,
                            method=urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    return resp.content
