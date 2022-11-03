@staticmethod
def ip_geolocation_info(ip_add):
    ret_dict = {}
    #first...check to see if we have the info in memcache
    keyy = ip_add + "_geolocation_info"
    val = memcache.get(keyy)
    if not val is None:
        return json.loads(val)

    #second...try to hit iplocation.net

    req_headers = {}
    req_headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    req_headers["accept-language"] = "en-US,en;q=0.8"
    req_headers["cache-control"] = "max-age=0"
    req_headers["content-type"] = "application/x-www-form-urlencoded"
    req_headers["origin"] = "https://www.iplocation.net"
    req_headers["referer"] = "https://www.iplocation.net/"
    req_headers["upgrade-insecure-requests"] = "1"
    req_headers["user-agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454.101 Chrome/45.0.2454.101 Safari/537.36"

    form_fields = {}
    form_fields["query"] = ip_add
    form_fields["submit"] = "Query"

    urll = "https://www.iplocation.net/"

    try:
        resp = urlfetch.fetch(
            url=urll,
            method=urlfetch.POST,
            payload=urllib.urlencode(form_fields),
            headers=req_headers,
            deadline=30
        )

        if resp.status_code == 200:
            page = BeautifulSoup(resp.content)
            main_div = page.find(id="geolocation")

            tables = main_div.find_all("table", recursive=False)
            state_dict = {}

            for table in tables:
                trs = table.find_all("tr", recursive=False)

                tr_count = 0
                for tr in trs:
                    if tr_count == 3:
                        tds = tr.find_all("td", recursive=False)
                        td_count = 0
                        for td in tds:
                            if td_count == 2:
                                state = td.get_text()
                                logging.info(state)
                                state_abbrev = Helpers.abbreviate_state(state)


                                if not state in state_dict.keys():
                                    state_dict[state_abbrev] = 0

                                state_dict[state_abbrev] += 1

                            td_count += 1

                    tr_count += 1

            max = -1
            max_key = ""

            done = False
            while not done:
                keys = state_dict.keys()
                changed = False
                for qey in keys:
                    if state_dict[qey] > max:
                        max = state_dict[qey]
                        max_key = qey
                        changed = True
                done = not changed

            ret_dict["state"] = max_key

    except:
        #try to hit infosniper.net

        del req_headers["content-type"]
        del req_headers["origin"]
        del req_headers["referer"]

        resp = urlfetch.fetch(
            url=urll,
            method=urlfetch.GET,
            headers=req_headers,
            deadline=30
        )

        if resp.status_code == 200:
            dom = BeautifulSoup(resp.content)

            td_count = 0
            tds = dom.find_all("td", {"class": "content-td2"})

            for td in tds:
                if td_count == 5:
                    txt = td.get_text()
                    idx = txt.index("(")
                    state = ""
                    char_cnt = 0
                    while char_cnt < idx - 1:
                        state += str(txt[char_cnt])
                        char_cnt += 1

                    state_abbrev = Helpers.abbreviate_state(state)
                    ret_dict["state"] = state_abbrev

                td_count += 1


    if "state" in ret_dict.keys():
        memcache.set(key=keyy, value=json.dumps(ret_dict), time=60 * 60 * 24)
        return ret_dict
    else:
        ret_dict["state"] = "CA"
        return ret_dict
