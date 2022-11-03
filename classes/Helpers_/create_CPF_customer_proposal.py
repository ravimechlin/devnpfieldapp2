@staticmethod
def create_CPF_customer_proposal(entry):
    req_headers = Helpers.get_CPF_session_headers()
    keyy = "req_headers_for_entry_" + entry.identifier
    val = json.dumps(req_headers)
    memcache.set(key=keyy, value=val, time=1800)

    req_headers3 = json.loads(json.dumps(req_headers))
    req_headers3["Accept"] = "application/json, text/javascript, */*; q=0.01"
    req_headers3["Accept-Encoding"] = "gzip,deflate,sdch"
    req_headers3["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    req_headers3["Host"] = "tools.cleanpowerfinance.com"
    req_headers3["Origin"] = "https://tools.cleanpowerfinance.com"
    req_headers3["Referrer"] = "https://tools.cleanpowerfinance.com/quoting/customer/eligibility/id/" + str(entry.customer_cpf_id)
    req_headers3["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"
    req_headers3["X-Requested-With"] = "XMLHttpRequest"

    #create the proposal
    form_fields = {}
    form_fields["name"] = "FINAL"
    form_fields["proposal_uuid"] = "24ac2fe4-c83b-11e4-9c1c-4040ba855862"
    form_fields["optimization"] = ""
    form_fields["offset_percentage"] = "80"
    form_fields["tier_to_offset"] = "1"
    form_fields["tier_month"] = "1"

    create_proposal_url = "https://tools.cleanpowerfinance.com/quoting/customer/createproposal/id/" + str(entry.customer_cpf_id)
    req_headers4 = json.loads(json.dumps(req_headers3))
    req_headers4["X-Requested-With"] = "XMLHttpRequest"
    req_headers4["Referrer"] = "https://tools.cleanpowerfinance.com/quoting/customer/"

    resp = urlfetch.fetch(
        url=create_proposal_url,
        method=urlfetch.POST,
        payload=urllib.urlencode(form_fields),
        deadline=30,
        headers=req_headers4,
        follow_redirects=False
    )
