@staticmethod
def get_mosaic_session_headers():
    today = datetime.today()
    keyy = "mosaic_session_id_" + str(today.month) + "_" + str(today.day) + "_" + str(today.year)

    val = memcache.get(keyy)
    if val is None:

        play_session_id = ""
        csrf_token = ""

        while (play_session_id == "") or (csrf_token == ""):
            ua_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"}

            #hit the login page and pickup the token
            resp = urlfetch.fetch(url="https://solcius.financing.joinmosaic.com/sign-in",
                deadline=30,
                method=urlfetch.GET)

            try:
                val = resp.header_msg.getheaders("Set-Cookie")[0]
                if not val == "":

                    if val.index("PLAY_SESSION") >= 0:
                        logging.info("here")
                        play_session_id = val[val.index("\""):val.index(";")]
                        logging.info(play_session_id)

                    page_dom = BeautifulSoup(resp.content)

                    input_els = page_dom.find_all("input")
                    tk = None
                    for input_el in input_els:
                        try:
                            nayme = str(input_el["name"])
                            if nayme == "csrfToken":
                                try:
                                    tk = input_el["value"]
                                except:
                                    tk = tk
                        except:
                            tk = tk

                    if not tk is None:
                        csrf_token = tk

            except:
                play_session_id = " "
                csrf_token = ""

        mosaic_creds = Helpers.get_current_mosaic_credentials()

        #perform the CPF login
        form_fields = {}
        form_fields["email"] = mosaic_creds["username"]
        form_fields["password"] = mosaic_creds["password"]
        form_fields["submit"] = ""
        form_fields["csrfToken"] = csrf_token
        resp2 = urlfetch.fetch(
            url="https://solcius.financing.joinmosaic.com/sign-in",
            method=urlfetch.POST,
            payload=urllib.urlencode(form_fields),
            deadline=30,
            headers = {
                'Cookie': "PLAY_SESSION=" + play_session_id,
            },
            follow_redirects=True
        )
        logging.info(resp2.status_code)
        Helpers.send_email("rnirnber@gmail.com", "try", (resp2.content))
        login_success = False
        partner_session_id = ""
        try:
            if resp2.status_code > 300 and resp2.status_code < 400:
                login_success = True
            else:
                login_success = False

            if login_success:
                header_val = resp2.header_msg.getheaders("Set-Cookie")[0]

                if not header_val == "":
                    header_val = header_val.replace("partner-sessionId=", "")
                    header_val = header_val[0:header_val.index(";")]
                    partner_session_id = header_val
        except:
            login_success = False

        logging.info(login_success)
        logging.info(play_session_id)
        logging.info(partner_session_id)
        if login_success and (not play_session_id == "" and (not partner_session_id == "")):
            keyy = keyy + "_KILL_THIS_FUNCTIONALITY2"
            memcache.set(key=keyy, value="ds", time=(60 * 60 * 24))
            cookie_str = "PLAY_SESSION=" + play_session_id + "; partner-sessionId=" + partner_session_id
            return {'Cookie': cookie_str, "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"}
        else:
            return {'Cookie': 'foo=bar'}

    else:
        return {'Cookie': val, "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"}

