@staticmethod
def create_CPF_customer_proposal5(entry, proposal_id):
    req_headers = None
    keyy = "req_headers_for_entry_" + entry.identifier
    val = memcache.get(keyy)
    if not val is None:
        req_headers = json.loads(val)
    else:
        req_headers = Helpers.get_CPF_session_headers()

    proposal_payment_url_GET = "https://tools.cleanpowerfinance.com/quoting/proposal/payment/id/" + proposal_id

    req_headers3 = json.loads(json.dumps(req_headers))
    req_headers3["Accept"] = "application/json, text/javascript, */*; q=0.01"
    req_headers3["Accept-Encoding"] = "gzip,deflate,sdch"
    req_headers3["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    req_headers3["Host"] = "tools.cleanpowerfinance.com"
    req_headers3["Origin"] = "https://tools.cleanpowerfinance.com"
    req_headers3["Referrer"] = "https://tools.cleanpowerfinance.com/quoting/customer/eligibility/id/" + str(entry.customer_cpf_id)
    req_headers3["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"
    req_headers3["X-Requested-With"] = "XMLHttpRequest"

    json_str = memcache.get("payment_methods_info_for_" + entry.identifier)
    payment_methods_info = json.loads(json_str)

    next_post_payment_methods = json.loads(memcache.get("next_post_payment_methods_for_" + entry.identifier))
    form_fields = {}
    req_data = {}

    for payment_method_info in payment_methods_info:
        if payment_method_info["slotNum"] == 3:
            next_post_payment_methods["3"]["monthlySavings"] = float(payment_method_info["monthlySavings"])
            next_post_payment_methods["3"]["postSolarMonthlyCost"] = float(payment_method_info["postSolarMonthlyCost"])
            next_post_payment_methods["3"]["grossSystemPrice"] = payment_method_info["grossSystemPrice"]
            next_post_payment_methods["3"]["actualGrossMargin"] = float(payment_method_info["actualGrossMargin"])
            next_post_payment_methods["3"]["lifetimeSavings"] = payment_method_info["lifetimeSavings"]
            next_post_payment_methods["3"]["pricePerWatt"] = payment_method_info["pricePerWatt"]
            next_post_payment_methods["3"]["monthlyFinancingPayment"] = payment_method_info["monthlyFinancingPayment"]
            next_post_payment_methods["3"]["margin"] = payment_method_info["margin"]


            req_data["paymentMethods"] = next_post_payment_methods

            form_fields["payment_data"] = json.dumps(req_data)

            req_headers7 = json.loads(json.dumps(req_headers3))
            resp = urlfetch.fetch(
                url="https://tools.cleanpowerfinance.com/quoting/proposal/save-payment-methods/id/" + proposal_id,
                method=urlfetch.POST,
                payload=urllib.urlencode(form_fields),
                deadline=30,
                headers=req_headers7,
                follow_redirects=True
            )

            req_headers8 = json.loads(json.dumps(req_headers))
            req_headers8["Referrer"] = proposal_payment_url_GET

            doc_gen_url = "https://tools.cleanpowerfinance.com/quoting/proposal/generate-documents/id/" + str(proposal_id)
            resp = urlfetch.fetch(
                url=doc_gen_url,
                method=urlfetch.GET,
                deadline=30,
                headers=req_headers8,
                follow_redirects=True
            )

            docs_ajax_url = "https://tools.cleanpowerfinance.com/quoting/customer/documents-data/id/" + str(entry.customer_cpf_id)
            resp = urlfetch.fetch(
                url=docs_ajax_url,
                method=urlfetch.GET,
                deadline=30,
                headers=req_headers8,
                follow_redirects=True
            )

            docs_json = json.loads(resp.content.strip())

            docs_signature_POST_url = "https://tools.cleanpowerfinance.com/quoting/proposal/send-for-signature/id/" + proposal_id

            #get the homeowner packet doc ID

            unknown_key = "unknown key"
            for keyy in docs_json["results"]["proposals"][proposal_id]["revisions"].keys():
                unknown_key = keyy

            rev_id = None
            for keyy in docs_json["results"]["proposals"][proposal_id]["revisions"][unknown_key]["documents"].keys():
                if docs_json["results"]["proposals"][proposal_id]["revisions"][unknown_key]["documents"][keyy]["type"] == "packet_homeowner":
                    rev_id = str(docs_json["results"]["proposals"][proposal_id]["revisions"][unknown_key]["documents"][keyy]["id"])

            form_fields = {}
            form_fields["docs_" + proposal_id + "[" + rev_id + "][signers][HomeownerPrimarySigner][id]"] = entry.customer_email.split("@")[0] + "@" + "raymondnirnberger.com"
            form_fields["docs_" + proposal_id + "[" + rev_id + "][signers][HomeownerPrimarySigner][role]"] = "HomeownerPrimarySigner"
            form_fields["inperson_" + proposal_id] = "false"

            resp = urlfetch.fetch(
                url=docs_signature_POST_url,
                method=urlfetch.POST,
                payload=urllib.urlencode(form_fields),
                deadline=30,
                headers=req_headers7,
                follow_redirects=True
            )


            form_fields = {}
            form_field_keys = [
                "movingAwayNextUrl",
                "saveTriggeredByChevron",
                "chevronUrl",
                "ctype",
                "ccompany",
                "newbuild",
                "csalutation",
                "cfirstname",
                "clastname",
                "cphone1",
                "cemail",
                "csecondarysalutation",
                "csecondaryfirstname",
                "csecondarylastname",
                "csecondaryphone",
                "csecondaryemail",
                "caddress1",
                "caddress2",
                "czip",
                "ccounty",
                "cstate",
                "ccity",
                "has_no_mailing_address",
                "caddress1_mail",
                "caddress2_mail",
                "czip_mail",
                "ccounty_mail",
                "cstate_mail",
                "ccity_mail",
                "ftaxrate",
                "staxrate",
                "hmofficepercent",
                "showAdditionalInfo",
                "cphone2",
                "alternative_email",
                "est_start_install_date",
                "cbudget",
                "additional_information",
                "clickname"
            ]

            for key in form_field_keys:
                form_fields[key] = ""

            form_fields["ctype"] = "1"
            form_fields["newbuild"] = "0"
            form_fields["cfirstname"] = entry.customer_first_name
            form_fields["clastname"] = entry.customer_last_name
            form_fields["cphone1"] = Helpers.format_phone_number(entry.customer_phone)
            dob_feelds = str(entry.customer_dob).split("-")
            dob_str = "-".join([dob_feelds[1], dob_feelds[2], dob_feelds[0]])
            form_fields["additional_information"] = "DOB:\n" + dob_str + "\nPrice per KwH:\n" + entry.customer_kwh_price + "\n\n"


            #
            #form_fields["cemail"] = entry.customer_email
            #
            #temp_email = "p_" + str(zlib.crc32(entry.identifier)).replace("-", "neg") + "@" + "citymail.email"
            #temp_email = "p_" + str(zlib.crc32(entry.identifier)).replace("-", "neg") + "@" + "raymondnirnberger.com"
            temp_email = entry.customer_email.split("@")[0] + "@" + "raymondnirnberger.com"
            #temp_email = entry.customer_email.split("@")[0] + "@" + "raymondnirnberger.com"
            form_fields["cemail"] = temp_email
            form_fields["caddress1"] = entry.customer_address
            form_fields["czip"] = entry.customer_postal

            form_fields["ccounty"] = Helpers.get_county_from_city_and_state_and_zip(entry.customer_city, entry.customer_state, entry.customer_postal)

            form_fields["cstate"] = entry.customer_state
            form_fields["ccity"] = entry.customer_city
            form_fields["has_no_mailing_address"] = "on"
            form_fields["czip_mail"] = entry.customer_postal
            form_fields["ftaxrate"] = "28.000"
            form_fields["staxrate"] = "9.300"
            form_fields["hmofficepercent"] = "0"
            form_fields["showAdditionalInfo"] = "true"
            form_fields["cbudget"] = "0"
            form_fields["clickname"] = "SaveOnly"

            form_fields["cemail"] = entry.customer_email

            req_headers["Content-Type"] = "application/x-www-form-urlencoded"

            resp = urlfetch.fetch(
                url="https://tools.cleanpowerfinance.com/quoting/customer/customer-info/id/" + str(entry.customer_cpf_id),
                method=urlfetch.POST,
                payload=urllib.urlencode(form_fields),
                deadline=30,
                headers = req_headers,
                follow_redirects=False
            )

