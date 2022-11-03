@staticmethod
def provision_google_apps_account(email, first_name, last_name):
    req_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    form_fields = {"email": email, "first_name": first_name, "last_name": last_name}
    resp = urlfetch.fetch(
            url="https://script.google.com/macros/s/AKfycbw_KNXM9BfVqjIP4Lo_BeInaV0MSjrYTDKWscmVUNwrgC6TpJc/exec",
            method=urlfetch.POST,
            payload=urllib.urlencode(form_fields),
            deadline=30,
            headers = req_headers,
            follow_redirects=True)
