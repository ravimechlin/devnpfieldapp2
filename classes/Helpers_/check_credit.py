@staticmethod
def check_credit(app_entry):
    req_headers = {}
    req_headers["Content-Type"] = "application/x-www-form-urlencoded"

    form_fields = {}
    form_fields["FirstName"] = app_entry.customer_first_name
    form_fields["LastName"] = app_entry.customer_last_name
    form_fields["Address"] = app_entry.customer_address
    form_fields["City"] = app_entry.customer_city
    form_fields["State"] = app_entry.customer_state
    form_fields["Postal"] = app_entry.customer_postal

    #resp = urlfetch.fetch(
    #    url="http://130.211.156.34:8081/CheckCredit",
    #    method=urlfetch.POST,
    #    payload=urllib.urlencode(form_fields),
    #    deadline=40,
    #    headers=req_headers,
    #    follow_redirects=False)

    def save_bad_check():
        cc = CreditCheck(
            identifier=Helpers.guid(),
            field_app_identifier=app_entry.identifier,
            success=False,
            score=-1,
            last_four=-1,
            recorded_dt=Helpers.pacific_now()
        )
        cc.put()

    try:
        # put back loading of resp.content and uncomment resp above
        jaysawn = json.loads("FOOOOOO")
        if jaysawn["success"] == True:
            cc = CreditCheck(
                identifier=Helpers.guid(),
                field_app_identifier=app_entry.identifier,
                success=True,
                score=int(jaysawn["score"]),
                last_four=int(jaysawn["last_four"]),
                recorded_dt=Helpers.pacific_now()
            )
            cc.put()
            return cc.score
        else:
            save_bad_check()
    except:
        save_bad_check()
        req_headers = req_headers

    return None


