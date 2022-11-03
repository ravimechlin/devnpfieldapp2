@staticmethod
def get_CPF_session_headers():
    today = datetime.today()
    keyy = "cpf_php_session_id_" + str(today.month) + "_" + str(today.day) + "_" + str(today.year)

    val = memcache.get(keyy)
    if val is None:

        php_session_id = ""
        while php_session_id == "":

            #pick up a PHP session ID
            resp = urlfetch.fetch(url="https://tools.cleanpowerfinance.com/user/login",
                deadline=30,
                method=urlfetch.GET)

            try:
                val = resp.header_msg.getheaders("Set-Cookie")[0]

                if not val == "":

                    if val.index("PHPSESSID") >= 0:

                        php_session_id = val[0:val.index(";")]
            except:
                php_session_id = ""


        cpf_creds = Helpers.get_current_CPF_credentials()

        #perform the CPF login
        form_fields = {}
        form_fields["username"] = cpf_creds["username"]
        form_fields["password"] = cpf_creds["password"]

        resp2 = urlfetch.fetch(
            url="https://tools.cleanpowerfinance.com/user/login",
            method=urlfetch.POST,
            payload=urllib.urlencode(form_fields),
            deadline=30,
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': php_session_id
            },
        )
        new_sess_id = False
        login_success = False
        try:
            header_val = resp2.header_msg.getheaders("Set-Cookie")[0]

            if not header_val == "":
                if not val.index("PHPSESSID") >= 0:
                   new_sess_id = True
        except:
            login_success = True

        login_success = (not new_sess_id)

        final_url = ""
        if login_success:

            try:
                final_url = getattr(resp2, "final_url")
                if final_url is None:
                    login_success = False
            except:
                login_success = False

            login_success = login_success and (not (final_url == ""  or final_url is None))

        if login_success:
            keyy = keyy + "_KILL_THIS_FUNCTIONALITY"
            memcache.set(key=keyy, value=php_session_id, time=(60 * 60 * 24))
            return {'Cookie': php_session_id, "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"}
        else:
            return {'Cookie': 'foo=bar'}

    else:
        return {'Cookie': val, "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"}

