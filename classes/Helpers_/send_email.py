@staticmethod
def send_email(to, subject, message, attachment_data=None, ccs=[]):
    message = message.replace(u'\xa0', '')
    attachments = []
    content_types = []
    filenames = []

    if not attachment_data is None:
        if "data" in attachment_data.keys() and "content_types" in attachment_data.keys() and "filenames" in attachment_data.keys():
            attachments = attachment_data["data"]
            content_types = attachment_data["content_types"]
            filenames = attachment_data["filenames"]

    apps_script_mailer_url = Helpers.get_apps_script_mailer_url()

    form_fields = {}
    form_fields["to"] = to.replace(u'\u202d', '').replace(u"\u202E", "").replace(u"\u202C", "")

    email_address = form_fields["to"]

    to_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pause_emails_" + email_address)

    form_fields["subject"] = subject.replace(u'\u202d', '').replace(u"\u202E", "").replace(u"\u202C", "")
    form_fields["message"] = message.replace(u'\u202d', '').replace(u"\u202E", "").replace(u"\u202C", "")
    if len(ccs) > 0:
        form_fields["cc"] = ','.join(ccs)

    if len(attachments) > 0 and len(content_types) > 0 and len(filenames) > 0:
        form_fields["attachments"] = json.dumps(attachments)
        form_fields["attachment_content_types"] = json.dumps(content_types)
        form_fields["attachment_filenames"] = json.dumps(filenames)

    form_data = urllib.urlencode(form_fields)

    if to_kv is None:
        resp = urlfetch.fetch(
                                url=apps_script_mailer_url,
                                payload=form_data,
                                deadline=55,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        return resp.content
    return ""

