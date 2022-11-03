@staticmethod
def create_CPF_customer_proposal4(entry, proposal_id):
    req_headers = None
    keyy = "req_headers_for_entry_" + entry.identifier
    val = memcache.get(keyy)
    if not val is None:
        req_headers = json.loads(val)
    else:
        req_headers = Helpers.get_CPF_session_headers()

    req_headers3 = json.loads(json.dumps(req_headers))
    req_headers3["Accept"] = "application/json, text/javascript, */*; q=0.01"
    req_headers3["Accept-Encoding"] = "gzip,deflate,sdch"
    req_headers3["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    req_headers3["Host"] = "tools.cleanpowerfinance.com"
    req_headers3["Origin"] = "https://tools.cleanpowerfinance.com"
    req_headers3["Referrer"] = "https://tools.cleanpowerfinance.com/quoting/customer/eligibility/id/" + str(entry.customer_cpf_id)
    req_headers3["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36"
    req_headers3["X-Requested-With"] = "XMLHttpRequest"


    inline_json = json.loads(memcache.get("inline_json_for_" + entry.identifier))

    next_post_payment_methods = {}
    next_post_payment_methods["2"] = inline_json["customer"]["proposal"]["paymentMethods"]["2"]

    proposal_payment_url_POST = "https://tools.cleanpowerfinance.com/quoting/proposal/update-payment-method/id/" + proposal_id + "/slotNum/"

    json_to_POST = {}
    json_to_POST["id"] = int(proposal_id)
    json_to_POST["name"] = "FINAL"
    json_to_POST["isFinanced"] = 0
    json_to_POST["marginUseOverride"] = 1
    json_to_POST["isLocked"] = False
    json_to_POST["quoteId"] = inline_json["customer"]["proposal"]["quoteId"]
    json_to_POST["defaultMargin"] = inline_json["customer"]["proposal"]["defaultMargin"]
    json_to_POST["systemSize"] = round(inline_json["customer"]["proposal"]["systemSize"], 2)
    json_to_POST["paymentMethods"] = {}

    target_payment_method = inline_json["customer"]["proposal"]["paymentMethods"]["3"]
    json_to_POST["paymentMethods"]["id"] = target_payment_method["id"]
    json_to_POST["paymentMethods"]["slotNum"] = target_payment_method["slotNum"]
    proposal_payment_url_POST += str(target_payment_method["slotNum"])
    json_to_POST["paymentMethods"]["isPrimary"] = 1
    json_to_POST["paymentMethods"]["financingProductId"] = target_payment_method["financingProductId"]
    json_to_POST["paymentMethods"]["financingProductName"] = "GD 1 PPA Monthly"
    json_to_POST["paymentMethods"]["canPricingBeEditedByUser"] = True
    json_to_POST["paymentMethods"]["financingMethodId"] = target_payment_method["financingMethodId"]
    json_to_POST["paymentMethods"]["financingProductType"] = target_payment_method["financingProductType"]
    json_to_POST["paymentMethods"]["financingFormulaType"] = target_payment_method["financingFormulaType"]
    json_to_POST["paymentMethods"]["calfirstAPIResponse"] = target_payment_method["calfirstAPIResponse"]
    json_to_POST["paymentMethods"]["term"] = target_payment_method["term"]
    json_to_POST["paymentMethods"]["hasSibling"] = target_payment_method["hasSibling"]
    json_to_POST["paymentMethods"]["whichSibling"] = target_payment_method["whichSibling"]
    json_to_POST["paymentMethods"]["actualGrossMargin"] = target_payment_method["actualGrossMargin"]
    json_to_POST["paymentMethods"]["initialPayment"] = target_payment_method["initialPayment"]
    json_to_POST["paymentMethods"]["preSolarMonthlyCost"] = target_payment_method["preSolarMonthlyCost"]
    json_to_POST["paymentMethods"]["postSolarMonthlyCost"] = target_payment_method["postSolarMonthlyCost"]
    json_to_POST["paymentMethods"]["monthlySavings"] = target_payment_method["monthlySavings"]
    json_to_POST["paymentMethods"]["lifetimeSavings"] = target_payment_method["lifetimeSavings"]
    json_to_POST["paymentMethods"]["paybackPeriod"] = target_payment_method["paybackPeriod"]
    json_to_POST["paymentMethods"]["downPayment"] = target_payment_method["downPayment"]
    json_to_POST["paymentMethods"]["annualIncrease"] = target_payment_method["annualIncrease"]
    json_to_POST["paymentMethods"]["billingSurcharge"] = target_payment_method["billingSurcharge"]
    json_to_POST["paymentMethods"]["margin"] = target_payment_method["margin"]
    json_to_POST["paymentMethods"]["grossSystemPrice"] = target_payment_method["grossSystemPrice"]
    json_to_POST["paymentMethods"]["pricePerWatt"] = target_payment_method["pricePerWatt"]
    json_to_POST["paymentMethods"]["pricePerkwh"] = "0." + entry.customer_kwh_price.replace(".", "")
    json_to_POST["paymentMethods"]["monthlyFinancingPayment"] = target_payment_method["monthlyFinancingPayment"]
    json_to_POST["paymentMethods"]["amountFinanced"] = target_payment_method["amountFinanced"]
    json_to_POST["paymentMethods"]["rate"] = target_payment_method["rate"]
    json_to_POST["paymentMethods"]["proposalId"] = target_payment_method["proposalId"]
    json_to_POST["paymentMethods"]["pencilChanged"] = "pricePerkwh"

    next_post_payment_methods["3"] = json.loads(json.dumps(json_to_POST["paymentMethods"]))

    next_post_payment_methods["4"] = inline_json["customer"]["proposal"]["paymentMethods"]["4"]

    form_fields = {}
    form_fields["payment_method_data"] = json.dumps(json_to_POST)

    req_headers6 = json.loads(json.dumps(req_headers3))
    req_headers6["Referrer"] = "https://tools.cleanpowerfinance.com/quoting/proposal/payment/id/" + proposal_id

    resp = urlfetch.fetch(
        url=proposal_payment_url_POST,
        method=urlfetch.POST,
        payload=urllib.urlencode(form_fields),
        deadline=30,
        headers=req_headers6,
        follow_redirects=True
    )

    form_fields = {}
    next_post_payment_methods["3"]["initialPayment"] = int(float(next_post_payment_methods["3"]["initialPayment"]))
    next_post_payment_methods["3"]["pricePerkwh"] =  float(next_post_payment_methods["3"]["pricePerkwh"])
    next_post_payment_methods["3"]["margin"] = float(next_post_payment_methods["3"]["margin"])

    try:
        del next_post_payment_methods["3"]["proposalId"]
        del next_post_payment_methods["3"]["pencilChanged"]


        del next_post_payment_methods["4"]["disqualified"]
        del next_post_payment_methods["4"]["disqualifiedMessage"]
        del next_post_payment_methods["4"]["pricePerWattFormatted"]
        del next_post_payment_methods["4"]["actualGrossMarginFormatted"]
        del next_post_payment_methods["4"]["pricePerkwhFormatted"]
        del next_post_payment_methods["4"]["monthlySavingsFormatted"]
        del next_post_payment_methods["4"]["preSolarMonthlyCostFormatted"]
        del next_post_payment_methods["4"]["financing_product_elements"]
        del next_post_payment_methods["4"]["monthlyFinancingPaymentFormatted"]
        del next_post_payment_methods["4"]["grossSystemPriceFormatted"]
        del next_post_payment_methods["4"]["postSolarMonthlyCostFormatted"]
        del next_post_payment_methods["4"]["initialPaymentFormatted"]
        del next_post_payment_methods["4"]["lifetimeSavingsFormatted"]

    except:
        form_fields = form_fields

    updated_json = json.loads(resp.content)
    #payment_methods_info = json.loads(updated_json["paymentMethodData"])
    memcache.set(key="payment_methods_info_for_" + entry.identifier, value=updated_json["paymentMethodData"], time=60 * 30)
    memcache.set(key="next_post_payment_methods_for_" + entry.identifier, value=json.dumps(next_post_payment_methods), time=60 * 30)

