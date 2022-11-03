@staticmethod
def create_CPF_customer_proposal3(entry, proposal_id):
    req_headers = None
    keyy = "req_headers_for_entry_" + entry.identifier
    val = memcache.get(keyy)
    if not val is None:
        req_headers = json.loads(val)
    else:
        req_headers = Helpers.get_CPF_session_headers()


    proposal_payment_url_GET = "https://tools.cleanpowerfinance.com/quoting/proposal/payment/id/" + proposal_id

    req_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    #req_headers["Accept-Encoding"] = "gzip, deflate, sdch"
    req_headers["Accept-Language"] = "en-US,en;q=0.8"
    req_headers["Cache-Control"] = "max-age=0"
    req_headers["Connection"] = "keep-alive"
    req_headers["Host"] = "tools.cleanpowerfinance.com"
    req_headers["Referer"] = "https://tools.cleanpowerfinance.com/quoting/proposal/energy/id/" + proposal_id
    req_headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/43.0.2357.81 Chrome/43.0.2357.81 Safari/537.36"
    logging.info(req_headers)
    #parse out the data from the inline JSON ont the payments page

    resp = urlfetch.fetch(
        url=proposal_payment_url_GET,
        method=urlfetch.GET,
        deadline=30,
        headers=req_headers,
        follow_redirects=True
    )
    proposals_payment_html = resp.content

    start_str = "var jsonRepresentation = "
    trimmed_html = proposals_payment_html[proposals_payment_html.index(start_str) + len(start_str):]
    trimmed_html = trimmed_html[0:trimmed_html.index("window.fmethod = new NewFinancingMethod")]
    trimmed_html = trimmed_html.strip()
    trimmed_html = trimmed_html[0:len(trimmed_html) - 1]

    #inline_json = json.loads(trimmed_html)
    keyy = "inline_json_for_" + entry.identifier
    memcache.set(key=keyy, value=trimmed_html, time=60 * 30)


@staticmethod
def create_CPF_customer_proposal2(entry):
    req_headers = None
    keyy = "req_headers_for_entry_" + entry.identifier
    val = memcache.get(keyy)
    if not val is None:
        req_headers = json.loads(val)
    else:
        req_headers = Helpers.get_CPF_session_headers()

    #get the proposal's ID'
    req_headers5 = json.loads(json.dumps(req_headers))
    cust_proposals_url = "https://tools.cleanpowerfinance.com/quoting/customer/proposals/id/" + str(entry.customer_cpf_id)

    resp = urlfetch.fetch(
        url=cust_proposals_url,
        method=urlfetch.GET,
        deadline=30,
        headers=req_headers5,
        follow_redirects=True
    )

    proposals_page_dom = BeautifulSoup(resp.content)

    proposal_els = proposals_page_dom.find_all(title="FINAL")
    href = None
    for proposal_el in proposal_els:
        try:
            href = proposal_el["href"]
        except:
            href = href

    proposal_id = href.split("/")[-1]
    return proposal_id

