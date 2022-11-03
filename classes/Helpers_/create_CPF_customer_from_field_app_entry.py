@staticmethod
def create_CPF_customer_from_field_app_entry(entry):

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
    #temp_email = entry.customer_email.split("@")[0] + "@" + "citymail.email"
    temp_email = entry.customer_email.split("@")[0] + "@" + "raymondnirnberger.com"
    form_fields["cemail"] = temp_email
    form_fields["caddress1"] = entry.customer_address
    form_fields["czip"] = entry.customer_postal

    form_fields["ccounty"] = Helpers.get_county_from_city_and_state_and_zip(entry.customer_city, entry.customer_state, entry.customer_postal)
    cust_county = form_fields["ccounty"]

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

    original_form_fields = json.loads(json.dumps(form_fields))

    req_headers = Helpers.get_CPF_session_headers()
    req_headers_copy = json.loads(json.dumps(req_headers))
    req_headers["Content-Type"] = "application/x-www-form-urlencoded"

    resp = urlfetch.fetch(
            url="https://tools.cleanpowerfinance.com/quoting/customer/customer-info/",
            method=urlfetch.POST,
            payload=urllib.urlencode(form_fields),
            deadline=30,
            headers = req_headers,
            follow_redirects=False)


    if resp.status_code == 302:
        redirect_url = ""
        while_count = 0
        try:

            while redirect_url == "":

                header_val = resp.header_msg.getheaders("Location")[0]

                if not header_val == "":

                    if header_val.index("customer") >= 0:

                        redirect_url = header_val

                while_count += 1

                if while_count >= 5:
                    Helpers.kill_current_cpf_session()
                    return -1

        except:
            Helpers.kill_current_cpf_session()
            return -1

        vals = redirect_url.split("/")
        cust_num = vals[-1]

        if cust_num.isdigit():

            cust_number = int(cust_num)
            entry.customer_cpf_id = cust_number
            entry.put()

    else:
        return -1

    form_fields = {}

    form_field_keys = [
        "movingAwayNextUrl",
        "saveTriggeredByChevron",
        "chevronUrl",
        "cutility1",
        "presolarrate1",
        "usage_entry_mode",
        "average_month_month_selector",
        "service_average_monthly_bill",
    ]

    base_key = "energyUsageMonth"
    sub_keys = ["euse", "ebill", "consumption_peak", "consumption_part", "consumption_off", "demand_peak", "demand_part", "demand_off"]

    for key in sub_keys:

        count = 1
        while count < 13:

            form_key = base_key + str(count) + "[" + key + "]"
            form_field_keys.append(form_key)
            form_field_keys.append(base_key + str(count) + "[month]")
            count = count + 1

    additional_form_field_keys = [
        "showEnergyAdditionalInfo",
        "service_voltage",
        "service_phase",
        "service_meter_number",
        "service_account_number",
        "service_customer_number",
        "service_customer_name",
        "clickname"
    ]

    form_field_keys = form_field_keys + additional_form_field_keys

    for key in form_field_keys:
        form_fields[key] = ""

    #hit the energy page with a GET request to retrieve to retrieve the rate id and utility company id

    energy_page_url = "https://tools.cleanpowerfinance.com/quoting/customer/energy/id/" + str(entry.customer_cpf_id)
    req_headers.pop("Content-Type", 0)

    resp = urlfetch.fetch(
            url=energy_page_url,
            method=urlfetch.GET,
            deadline=30,
            headers = req_headers,
            follow_redirects=True)

    energy_page_dom = BeautifulSoup(resp.content)

    rate_select_element = energy_page_dom.find(id="presolarrate1")

    rate_id = -999
    utility_company_id = -999

    # parse out the first rate ID

    if not rate_select_element is None:

        option_elements = rate_select_element.find_all("option")

        for option_element in option_elements:

            if rate_id == -999 and (not str(option_element) == ""):

                    if option_element.name.lower() == "option":

                        att_keys = option_element.attrs.keys()
                        att_keys2 = []

                        for att in att_keys:
                            att_keys2.append(att.lower())

                        if "selected" in att_keys2 and "value" in att_keys2:
                            rate_id = int(option_element["value"])



    # get the utility company ID

    utility_by_zipcode_url = "https://tools.cleanpowerfinance.com/dbaseadmin2/public/utilitiesbyzipcode?zipcode=" + entry.customer_postal + "&retrieveAllForState=0&standardize=1&maintainorder=1"

    resp = urlfetch.fetch(
        url=utility_by_zipcode_url,
        method=urlfetch.GET,
        deadline=30,
        headers = req_headers,
        follow_redirects=True
    )

    if resp.status_code == 200:

        data = json.loads(resp.content)

        if data["statusCode"] == 200 and data["success"]:

            if len(data["results"]) > 0:

                utility_company_id = int(data["results"][0].keys()[0])



        #proceed with fetching the energy usage for the customer's zip code and rate ID

        if (not rate_id == -999) and (not utility_company_id == -999):

            form_fields["cutility1"] = str(utility_company_id)
            form_fields["presolarrate1"] = str(rate_id)
            form_fields["usage_entry_mode"] = "average_bill"
            form_fields["average_month_month_selector"] = "0"
            form_fields["service_average_monthly_bill"] = "200.00"

            energy_usage_url = "https://tools.cleanpowerfinance.com/quoting/index/energy-usage-data?zipcode=" + entry.customer_postal + "&rate_id=" + str(rate_id) + "&usage_entry_mode=average_bill&building_type=residential&monthly_bill_month=0&average_bill=200.00"

            resp = urlfetch.fetch(
                url=energy_usage_url,
                method=urlfetch.GET,
                deadline=30,
                headers = req_headers,
                follow_redirects=True
            )

            usage_success = False

            if resp.status_code == 200:

                data = json.loads(resp.content)

                if data["statusCode"] == 200 and data["success"]:

                    usage_success = True
                    count = 1
                    while count < 13:
                        count_str = str(count)
                        form_fields["energyUsageMonth" + count_str + "[euse]"] = str(data["results"]["usage_months"][count_str]["value"])
                        form_fields["energyUsageMonth" + count_str + "[month]"] = count_str
                        form_fields["energyUsageMonth" + count_str + "[ebill]"] = str(data["results"]["bill_months"][count_str]["value"])
                        form_fields["energyUsageMonth" + count_str + "[month]"] = count_str
                        count = count + 1

            # parse out the rest from the DOM
            if usage_success:

                keys_in_dom = ["consumption_peak", "consumption_part", "consumption_off", "demand_peak", "demand_part", "demand_off"]

                for key_in_dom in keys_in_dom:

                    count = 1
                    while count < 13:

                        el = energy_page_dom.find(id="energyUsageMonth" + str(count) + "[" + key_in_dom + "]")
                        value = "0"

                        if not el is None:

                            value = str(int(str(el["value"])))

                        form_fields["energyUsageMonth" + str(count) + "[" + key_in_dom + "]"] = value
                        form_fields["energyUsageMonth" + str(count) + "[month]"] = str(count)
                        count = count + 1

                #copy the javascript logic to calculate the consumption_off fields
                original_euses = []
                count = 1
                while count < 13:

                    #get the original euses

                    el = energy_page_dom.find(id="energyUsageMonth" + str(count) + "[euse]")
                    value = "0"

                    if not el is None:
                        value = str(int(str(el["value"])))

                    original_euses.append(value)
                    count = count + 1


                #copying the js logic

                count = 1
                for original_euse in original_euses:

                    int_val_euse = int(original_euse)
                    int_val_peak = int(form_fields["energyUsageMonth" + str(count) + "[consumption_peak]"])
                    int_val_part = int(form_fields["energyUsageMonth" + str(count) + "[consumption_part]"])

                    new_consumption_offset = int_val_euse + (int_val_peak - int_val_part)
                    form_fields["energyUsageMonth" + str(count) + "[consumption_off]"] = str(new_consumption_offset)
                    count += 1

                form_fields["showEnergyAdditionalInfo"] = "true"
                form_fields["service_account_number"] = entry.customer_utility_account_number
                form_fields["clickname"] = "SaveOnly"

                req_headers["Content-Type"] = "application/x-www-form-urlencoded"
                req_headers["Host"] = "tools.cleanpowerfinance.com"
                req_headers["Origin"] = "https://tools.cleanpowerfinance.com"
                req_headers["Referer"] = "https://tools.cleanpowerfinance.com/quoting/customer/energy-usage/id/" + str(entry.customer_cpf_id)

                req_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                req_headers["Accept-Encoding"] = "gzip,deflate,sdch"
                req_headers["Accept-Language"] = "en-US,en;q=0.8"
                req_headers["Cache-Control"] = "max-age=0"
                req_headers["Connection"] = "keep-alive"
                req_headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"



                resp = urlfetch.fetch(
                    url="https://tools.cleanpowerfinance.com/quoting/customer/energy/id/" + str(entry.customer_cpf_id),
                    method=urlfetch.POST,
                    payload=urllib.urlencode(form_fields),
                    deadline=30,
                    headers = req_headers,
                    follow_redirects=True
                )

                req_headers.pop("Host", 0)
                req_headers.pop("Origin", 0)
                req_headers.pop("Referer",  0)
                req_headers.pop("Content-Type", 0)
                req_headers.pop("Accept", 0)
                req_headers.pop("Accept-Encoding", 0)
                req_headers.pop("Accept-Language", 0)
                req_headers.pop("Cache-Control", 0)
                req_headers.pop("Connection", 0)

                # Customer Eligibility Confirmation

                eligibility_init_url = "https://tools.cleanpowerfinance.com/quoting/customer/eligibility/id/" + str(entry.customer_cpf_id)

                form_fields = {}
                form_fields["customer-info-confirm"] = "1"
                form_fields["checkCredit"] = "0"
                form_fields["runRules"] = "0"
                form_fields["runTitle"] = "0"
                form_fields["cfirstname"] = entry.customer_first_name
                form_fields["clastname"] = entry.customer_last_name
                form_fields["csecondaryfirstname"] = ""
                form_fields["csecondarylastname"] = ""
                form_fields["caddress1"] = entry.customer_address
                form_fields["caddress2"] = ""
                form_fields["czip"] = entry.customer_postal
                form_fields["ccounty"] = cust_county
                form_fields["cstate"] = entry.customer_state
                form_fields["ccity"] = entry.customer_city
                form_fields["cutility1"] = str(utility_company_id)

                resp = urlfetch.fetch(
                    url=eligibility_init_url,
                    method=urlfetch.POST,
                    payload=urllib.urlencode(form_fields),
                    deadline=30,
                    headers = req_headers,
                    follow_redirects=True
                )

                req_headers2 = req_headers_copy

                # do a GET request to the page to pick up the CPF user's name
                resp = urlfetch.fetch(
                    url="https://tools.cleanpowerfinance.com/account/profile",
                    method=urlfetch.GET,
                    deadline=30,
                    headers = req_headers2,
                    follow_redirects=True
                )

                profile_page_dom = BeautifulSoup(resp.content)
                name_elements = profile_page_dom.find_all(id="firstname")
                name_el = ""

                for  name_element in name_elements:

                    try:

                        name_el = name_element["value"]

                    except:

                        name_el = name_el

                name_el += " "

                name_elements = profile_page_dom.find_all(id="lastname")

                for name_element in name_elements:

                    try:

                        name_el += name_element["value"]

                    except:

                        name_el = name_el

                email_el = ""

                resp = urlfetch.fetch(
                    url="https://tools.cleanpowerfinance.com/account/profile/editlogin/?width=300&height=370&random=" + str(int(time.time() * 1000)),
                    method=urlfetch.GET,
                    deadline=30,
                    headers = req_headers2,
                    follow_redirects=True
                )

                edit_page_dom = BeautifulSoup(resp.content)

                email_elements = edit_page_dom.find_all(id="loginEmail")
                email_el = ""

                for email_element in email_elements:

                    try:

                        email_el = email_element["value"]

                    except:

                        email_el = emai_el


                if (not email_el == "") and (not name_el == ""):

                    confirm_credit_check_url = "https://tools.cleanpowerfinance.com/quoting/customer/initiate-credit-check/id/" + str(entry.customer_cpf_id) + "?width=580&height=540&random="  + str(int(time.time() * 1000))

                    form_fields = {}
                    form_fields["isEmailCorrect"] = "true"
                    form_fields["homeownerEmailAddress"] = temp_email
                    form_fields["subject"] = u"Please submit your online credit application from - " + name_el
                    form_fields["emailMessage"] = "Dear " + entry.customer_first_name + " " + entry.customer_last_name + ",\n\nThank you for your interest in going solar! To get started, please follow the instructions below to submit your online credit application for review. The solar financing options available for your credit profile will be securely reported back to me. I will be notified of product availability only, not your credit scores or any other private information.\n\nSincerely,\n" + name_el + "\nSolcius, LLC\n" + name_el + " (New Power)\n" + email_el + "\n\n\nUnique Identifier: " + entry.identifier
                    form_fields["disclaimer"] = "1. Click on the link below (or cut and paste it into an Internet browser address bar)\n2. Enter the required information to complete the credit application. Applying with a co-applicant is recommended to increase qualification for the most competitive offerings. A co-application requires that both parties complete the application. \n3. Review the General Disclaimer and Privacy Policy\n4. Submit for credit review\n\n{LINK_HERE}"

                    req_headers3 = json.loads(json.dumps(req_headers))
                    req_headers3["Accept"] = "application/json, text/javascript, */*; q=0.01"
                    req_headers3["Accept-Encoding"] = "gzip,deflate,sdch"
                    req_headers3["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
                    req_headers3["Host"] = "tools.cleanpowerfinance.com"
                    req_headers3["Origin"] = "https://tools.cleanpowerfinance.com"
                    req_headers3["Referrer"] = "https://tools.cleanpowerfinance.com/quoting/customer/eligibility/id/" + str(entry.customer_cpf_id)
                    req_headers3["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"
                    req_headers3["X-Requested-With"] = "XMLHttpRequest"

                    resp = urlfetch.fetch(
                        url=confirm_credit_check_url,
                        method=urlfetch.POST,
                        payload=urllib.urlencode(form_fields),
                        deadline=30,
                        headers = req_headers3,
                        follow_redirects=True
                    )

                    entry.put()

                    return entry.customer_cpf_id

