@staticmethod
def send_static_html(recipient, subject, html_content):

    form_fields = {}
    form_fields["to"] = recipient
    form_fields["subject"] = subject

    new_html_str = ""
    for idx in range( len(html_content) ):
        try:
            ascee = html_content[idx].encode("ascii")
            new_html_str = new_html_str + ascee
        except:
            
            nothing = "nithing"

    form_fields["html"] = new_html_str

    urlfetch.fetch(
        url="https://script.google.com/macros/s/AKfycbxeTF7rDpYW17bY6B7ooHEbKYiQJrt6BxVmqgdlABiqwDcubeW6/exec",
        method=urlfetch.POST,
        payload=urllib.urlencode(form_fields),
        deadline=30,
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        })

