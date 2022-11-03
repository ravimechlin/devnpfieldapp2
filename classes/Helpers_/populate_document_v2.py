@staticmethod
def populate_document_v2(sig, initials, doc, app_entry, survey_booking, proposal, token, rep=None, incentive=None, utility_person=None, acct_num="", exp_year="", exp_month="", cvv=""):
    roof_stream = None
    buff2224 = None

    if proposal is None:
        proposal = CustomerProposalInfo(
            identifier=Helpers.guid(),
            field_app_identifier=app_entry.identifier,
            version=1
        )
        inf_dict = {}
        inf_dict["system_size"] = "0"
        inf_dict["panel_type"] = ""
        inf_dict["panel_qty"] = "0"
        inf_dict["new_panel_qty"] = "0"
        inf_dict["inverter_type"] = ""
        inf_dict["racking"] = ""
        proposal.info = json.dumps(inf_dict)

    market_identifier = "-1"
    ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
    if not ol is None:
        market_identifier = ol.parent_identifier

    funds = Helpers.list_funds()
    pricing_structures = Helpers.get_pricing_structures()
    proposal_dict = json.loads(proposal.info)
    panel_qty = proposal_dict["panel_qty"]
    if "new_panel_qty" in proposal_dict.keys():
        panel_qty = proposal_dict["new_panel_qty"]

    if exp_year == "":
        exp_year = "1970"

    if exp_month == "":
        exp_month = "01"

    if incentive == "None":
        incentive = None

    if incentive is None:
        incentive = ""
    if rep is None:
        rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)

    if rep is None:
        return

    import StringIO
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO

    from fpdf import FPDF
    from PyPDF2 import PdfFileWriter,PdfFileReader

    three_days = Helpers.next_business_days(Helpers.pacific_today(), 3)
    three_days = datetime(three_days.year, three_days.month, three_days.day) + timedelta(days=1)
    four_days = three_days.date()

    sp2_dt = app_entry.sp_two_time.date()
    sp2_dt = str(sp2_dt)
    sp2_split = sp2_dt.split("-")
    sp2_date = sp2_split[1] + "/" + sp2_split[2] + "/" + sp2_split[0]

    sp2_hour = app_entry.sp_two_time.hour
    sp2_min = app_entry.sp_two_time.minute
    sp2_ampm = "AM"
    if sp2_hour > 11:
        sp2_ampm = "PM"
    if sp2_hour > 12:
        sp2_hour -= 12
    sp2_hour = str(sp2_hour)
    sp2_min = str(sp2_min)
    if len(sp2_hour) == 1:
        sp2_hour = "0" + sp2_hour
    if len(sp2_min) == 1:
        sp2_min = "0" + sp2_min
    sp2_time = sp2_hour + ":" + sp2_min + " " + sp2_ampm

    annual_income = "0"
    monthly_mortgage = "0"
    income_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "annual_income_" + app_entry.identifier)
    if not income_kv is None:
        annual_income = income_kv.val
    mortgage_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "mortgage_payment_" + app_entry.identifier)
    if not mortgage_kv is None:
        monthly_mortgage = mortgage_kv.val

    cc = CreditCheck.first(CreditCheck.field_app_identifier == app_entry.identifier)
    last_four = ""
    if not cc is None:
        if cc.last_four > -1:
            last_four = str(cc.last_four)
            while len(last_four) < 4:
                last_four = "0" + last_four

    incentive = ""
    inc_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "incentive_option_" + app_entry.identifier)
    if not inc_kv is None:
        incentive = inc_kv.val

    additional_services = Helpers.read_setting("services_schedule")
    add_svcs = ""
    if "additional_svcs" in proposal_dict.keys():        
        for svc in proposal_dict["additional_svcs"]:
            for svc2 in additional_services:
                if svc2["value"] == svc["value"] and svc2["listed_in_docs_composer_additional_services"]:
                    add_svcs += svc2["value_friendly"]
                    add_svcs += "\n"

    custom_svcs = ""
    if "custom_svcs" in proposal_dict.keys():
        for custom_svc in proposal_dict["custom_svcs"]:
            custom_svcs += custom_svc["name"]
            custom_svcs += "\n"
            add_svcs += custom_svc["name"]
            add_svcs += "\n"

    az = ""
    if "azimuth" in proposal_dict.keys():
        az = proposal_dict["azimuth"]

    esa = ""
    if "estimated_slope_of_array" in proposal_dict.keys():
        esa = proposal_dict["estimated_slope_of_array"]

    is_cash = ("cash" in survey_booking.fund)
    is_financed = (not is_cash)

    values_dict = {
        "customer_signature": "sig",
        "customer_initials": "initials",
        "todays_date": str(Helpers.pacific_today()).replace("-", " / "),
        "three_business_days": str(Helpers.next_business_days(Helpers.pacific_today(), 3)).replace("-", " / "),
        "day_after_NOC": str(four_days).replace("-", " / "),
        "azimuth": az,
        "array_slope": esa,
        "cash_deal": ["", "X"][int(is_cash)],
        "financed_deal": ["", "X"][int(is_financed)],
        "fund_apr": "0.00%",
        "customer_first": app_entry.customer_first_name.strip().title(),
        "customer_last": app_entry.customer_last_name.strip().title(),
        "customer_name": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
        "customer_address": app_entry.customer_address,
        "customer_email": app_entry.customer_email,
        "customer_phone": Helpers.format_phone_number(app_entry.customer_phone),
        "customer_address_city_state": app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state.upper(),
        "customer_address_city_state_postal": app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state.upper() + " " + app_entry.customer_postal,
        "customer_city": app_entry.customer_city,
        "customer_city_state": app_entry.customer_city + ", " + app_entry.customer_state.upper(),
        "customer_city_state_postal": app_entry.customer_city + ", " + app_entry.customer_state.upper() + " " + app_entry.customer_postal,
        "customer_state": app_entry.customer_state.upper(),
        "customer_postal": app_entry.customer_postal,
        "customer_utility_number": app_entry.customer_utility_account_number,
        "customer_utility_number": app_entry.customer_utility_account_number,
        "customer_annual_income": annual_income,
        "customer_monthly_mortgage": monthly_mortgage,
        "last_four": last_four,
        "sp2_date": sp2_date,
        "sp2_time": sp2_time,
        "system_size": proposal_dict["system_size"],
        "panel_module": proposal_dict["panel_type"],
        "panel_qty": panel_qty,
        "inverter_module": proposal_dict["inverter_type"],
        "additional_services": add_svcs,
        "custom_addons": custom_svcs,
        "racking_type": proposal_dict["racking"],
        "system_image": "img",
        "incentive": incentive,
        "credit_card_number": "",
        "credit_card_expiration_month": "01",
        "credit_card_expiration_year": "1970",
        "credit_card_expiration_date": "01/70",
        "credit_card_cvv_num": "123",
        "utility_account_holder": utility_person,
        "contractor_signature": "---",
        "contractor_logo": "---",
        "rep_signature": "---",
        "rep_name": rep.first_name.strip().title() + " " + rep.last_name.strip().title(),
        "fund_one_cost": "$0.00",
        "fund_two_cost": "$0.00",
        "solar_area_only_checkbox": "",
        "full_reroof_checkbox": "",
        "roof_work_photo": "",
        "roofing_exclusions": "",
        "roofing_materials": "",
        "security_question": "",
        "security_answer": "",
        "docs_gen_timestamp": "",
        "docs_viewed_timestamp": "",
        "current_timestamp": "",
        "batch_id": "",
        "document_id": "",
        "titan_incentive": "n/a",
        "amps": "",
        "volts": "",
        "rep_license_number": "999999",
        "cosigner_name": "",
        "cosigner_signature": "",
        "cosigner_initials": "",
        "rep_phone": "",
        "cs_plan_price": "0",
        "cs_routing_num": "",
        "cs_checking_num": "",
        "cs_bank_name": ""
        
    }

    bank_details = KeyValueStoreItem.first(KeyValueStoreItem.keyy == app_entry.identifier + "_bank")
    if not bank_details is None:
        d = json.loads(bank_details.val)
        if "routing" in d.keys():
            values_dict["cs_routing_num"] = d["routing"]
        if "account" in d.keys():
            values_dict["cs_checking_num"] = d["account"]
        if "bank_name" in d.keys():
            values_dict["cs_bank_name"] = d["bank_name"]


    svc_file = GCSLockedFile("/CustomerService/bulk.json")
    svc_contents = svc_file.read()
    svc_file.unlock()
    if svc_contents is None:
        svc_contents = "[]"

    deserialized_svc = json.loads(svc_contents)
    for item in deserialized_svc:
        if item["field_app_identifier"] == app_entry.identifier:
            if int(item["price"]) > 0:
                values_dict["cs_plan_price"] = str(item["price"])

    cs_kv1 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "cosigner_name_" + app_entry.identifier)
    if not cs_kv1 is None:
        values_dict["cosigner_name"] = cs_kv1.val
    
    rep9 = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
    if not rep9 is None:
        values_dict["rep_phone"] = rep9.rep_phone
        license_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "l_num_" + rep9.identifier)
        if not license_kv is None:
            values_dict["rep_license_number"] = license_kv.val
    import hashlib

    titan_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "titan_incentive_" + app_entry.identifier)
    if not titan_kv is None:
        values_dict["titan_incentive"] = titan_kv.val + " - Provided by New Power, not Titan"

    for fund in funds:
        if fund["value"] == survey_booking.fund:
            apr = float(fund["apr"])
            apr *= float(100)
            apr = round(apr, 2)
            apr = str(apr)
            apr = apr + "%"
            values_dict["fund_apr"] = apr

    values_dict["batch_id"] = hashlib.md5(Helpers.guid()).hexdigest()
    values_dict["document_id"] = hashlib.md5(Helpers.guid()).hexdigest()
    
    values_dict["current_timestamp"] = str(Helpers.pacific_now()).split(".")[0]

    security_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == app_entry.identifier + "_secret_qa")
    if not security_kv is None:
        security_info = json.loads(security_kv.val)
        values_dict["security_question"] = security_info["question"]
        values_dict["security_answer"] = security_info["answer"]

    docs_gen_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "docs_gen_timestamp_" + app_entry.identifier)
    if not docs_gen_kv is None:
        values_dict["docs_gen_timestamp"] = docs_gen_kv.val
        
    cost_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "confirmed_roof_work_numbers_" + app_entry.identifier)
    if not cost_kv is None:
        cost_info = json.loads(cost_kv.val)
        values_dict["fund_one_cost"] = cost_info["fund_one_cost"]
        values_dict["fund_two_cost"] = cost_info["fund_two_cost"]

    viewed_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "docs_viewed_ts_" + app_entry.identifier)
    if not viewed_kv is None:
        values_dict["docs_viewed_timestamp"] = viewed_kv.val

    roof_item = RoofWorkItem.first(RoofWorkItem.field_app_identifier == app_entry.identifier)
    if not roof_item is None:
        roof_info = json.loads(roof_item.info)
        if roof_info["rep_selection_one"] == "solar_area_only":
            values_dict["solar_area_only_checkbox"] = "X"
        elif roof_info["rep_selection_one"] == "full_reroof":
            values_dict["full_reroof_checkbox"] = "X"

        values_dict["roofing_exclusions"] = roof_info["exclusions"]
        values_dict["roofing_materials"] = roof_info["material_question"]


    if not acct_num is None:
        values_dict["credit_card_number"] = acct_num
    if not exp_month is None:
        values_dict["credit_card_expiration_month"] = exp_month
    if not exp_year is None:
        values_dict["credit_card_expiration_year"] = exp_year
    if not cvv is None:
        values_dict["credit_card_cvv_num"] = cvv

    tod = values_dict["todays_date"].split(" / ")
    values_dict["todays_date"] = tod[1] + " / " + tod[2] + " / " + tod[0]
    three_b = values_dict["three_business_days"].split(" /")
    values_dict["three_business_days"] = three_b[1] + " / " + three_b[2] + " / " + three_b[0]
    four_days = values_dict["day_after_NOC"].split(" / ")
    values_dict["day_after_NOC"] = four_days[1] + " / " + four_days[2] + " / " + four_days[0]

    cost_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "confirmed_roof_work_numbers_" + app_entry.identifier)
    if not cost_kv is None:
        cost_info = json.loads(cost_kv.val)
        values_dict["fund_one_cost"] = cost_info["fund_one_cost"]
        values_dict["fund_two_cost"] = cost_info["fund_two_cost"]

    if not (values_dict["credit_card_expiration_month"] + values_dict["credit_card_expiration_year"]) == "011970":
        dt = datetime(int(values_dict["credit_card_expiration_year"]), int(values_dict["credit_card_expiration_month"]), 1).date()
        dt_vals = str(dt).split("-")
        values_dict["credit_card_expiration_date"] = dt_vals[1] + " / " + dt_vals[0]

    amps_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "miss_amps_" + app_entry.identifier)
    if not amps_kv is None:
        values_dict["amps"] = amps_kv.val

    volts_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "miss_volts_" + app_entry.identifier)
    if not volts_kv is None:
        values_dict["volts"] = volts_kv.val

    
    for s in additional_services:
        indicator = ""
        if "additional_svcs" in proposal_dict.keys():
            for ss in proposal_dict["additional_svcs"]:
                if ss["value"] == s["value"]:
                    indicator = "X"
        values_dict["has_service_" + s["value"]] = indicator

    retryParameters = gcs.RetryParams(initial_delay=0.2,
                                               max_delay=5.0,
                                               backoff_factor=2,
                                               max_retry_period=15,
                                               urlfetch_timeout=30)
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    cnt = 1
    idx = 0
    template_items = json.loads(doc.template_items)
    img_bytes = []
    page_buffers = []
    fonts_dict = {}
    bytes_to_close = []
    sig_initial_bytes_to_close = None
    cad_stream_to_close = None
    cad_buffer_to_close = None

    cosigner_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "cosigner_name_" + app_entry.identifier)
    cosigner_initials_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "cosigner_initials_" + app_entry.identifier)
    cosigner_sig_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "cosigner_signature_" + app_entry.identifier)


    while cnt <= doc.page_count:
        filename = bucket + "/Images/Docs/" + doc.token + "/300/" + str(cnt) + ".jpg"
        gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
        img_bytes.append(BytesIO(gcs_file.read()))
        gcs_file.close()
        img = Image.open(img_bytes[idx])

        filtered_items = []
        for item in template_items[idx]:
            add_item = True
            if item["value"] == "cosigner_initials":
                if cosigner_kv is None:
                    add_item = False
            if item["value"] == "cosigner_signature":
                if cosigner_kv is None:
                    add_item = False

            if add_item:
                filtered_items.append(item)

        template_items[idx] = filtered_items


        for item in template_items[idx]:
            sig_initial_bytes_to_close = None
            cad_stream_to_close = None
            cad_buffer_to_close = None

            for key in ["width", "height", "x", "y", "font_size"]:
                item[key] = Helpers.adjust_pixel_size(item[key], 612, 2550)

            if item["value"] in ["customer_signature", "customer_initials", "cosigner_signature", "cosigner_initials"]:
                bayse64 = None
                if item["value"] == "customer_signature":
                    bayse64 = sig
                elif item["value"] == "customer_initials":
                    bayse64 = initials
                elif item["value"] == "cosigner_signature":
                    bayse64 = cosigner_sig_kv.val
                elif item["value"] == "cosigner_initials":
                    bayse64 = cosigner_initials_kv.val

                sig_initial_bytes_to_close = BytesIO(base64.b64decode(bayse64))
                img2 = Image.open(sig_initial_bytes_to_close)
                img2 = img2.resize((item["width"], item["height"]), Image.ANTIALIAS)
                img.paste(img2, (item["x"], item["y"]), img2)

            elif item["value"] == "roof_work_photo":
                roofwork_item = RoofWorkItem.first(RoofWorkItem.field_app_identifier == app_entry.identifier)
                if not roofwork_item is None:
                    roof_info = json.loads(roofwork_item.info)                    
                    img_postfix = "reroof_photo"
                    if not roof_info["rep_selection_one"] == "full_reroof":
                        img_postfix = "solar_area_photo"

                    roof_f = GCSLockedFile("/Images/RoofWorkDetails/" + app_entry.identifier + "/" + img_postfix + ".jpg")

                    roof_stream = BytesIO(roof_f.read())
                    roof_f.unlock()

                    buff2224 = StringIO.StringIO()
                    roof_image = Image.open(roof_stream)
                    roof_image = roof_image.resize((item["width"], item["height"]), Image.ANTIALIAS)
                    roof_image.save(buff2224, "JPEG")
                    buff2224.seek(2)

                    cpy9 = Image.new("RGBA", roof_image.size, (255, 255, 255, 0))
                    width = cpy9.size[0]
                    height = cpy9.size[1]

                    w_cnt = 0
                    while w_cnt < width:
                        h_cnt = 0
                        while h_cnt < height:
                            pixel_data = roof_image.getpixel((w_cnt, h_cnt))
                            cpy9.putpixel((w_cnt, h_cnt), pixel_data)
                            h_cnt += 1
                        w_cnt += 1

                    img.paste(cpy9, (item["x"], item["y"]), cpy9)
                

            elif item["value"] == "system_image":
                filename2 = bucket + '/ProposalBlobs/' + app_entry.identifier + "_cad_photo." + proposal_dict["cad_photo"]["extension"]

                retryParameters = gcs.RetryParams(initial_delay=0.2,
                    max_delay=5.0,
                    backoff_factor=2,
                    max_retry_period=15,
                    urlfetch_timeout=30)

                gcs_file2 = gcs.open(filename2, 'r', retry_params=retryParameters)
                cad_stream_to_close = BytesIO(gcs_file2.read())
                gcs_file2.close()


                cad_buffer_to_close = StringIO.StringIO()
                cad_image = Image.open(cad_stream_to_close)
                cad_image = cad_image.resize((item["width"], item["height"]), Image.ANTIALIAS)
                cad_image.save(cad_buffer_to_close, "JPEG")
                cad_buffer_to_close.seek(2)

                cpy = Image.new("RGBA", cad_image.size, (255, 255, 255, 0))
                width = cpy.size[0]
                height = cpy.size[1]

                w_cnt = 0
                while w_cnt < width:
                    h_cnt = 0
                    while h_cnt < height:
                        pixel_data = cad_image.getpixel((w_cnt, h_cnt))
                        cpy.putpixel((w_cnt, h_cnt), pixel_data)
                        h_cnt += 1
                    w_cnt += 1

                img.paste(cpy, (item["x"], item["y"]), cpy)

            elif item["value"] in ["contractor_signature", "contractor_logo"]:
                sub_folder = item["value"].split("_")[1].title() + "s"
                bucket_name = os.environ.get('BUCKET_NAME',
                                             app_identity.get_default_gcs_bucket_name())

                bucket = '/' + bucket_name
                filename = bucket + '/MarketSettings/Contractors/' + sub_folder + '/' + market_identifier + '.jpg'

                retryParameters = gcs.RetryParams(initial_delay=0.2,
                                                  max_delay=5.0,
                                                  backoff_factor=2,
                                                  max_retry_period=15,
                                                  urlfetch_timeout=30)

                gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
                contractor_stream = BytesIO(gcs_file.read())
                gcs_file.close()

                buff222 = StringIO.StringIO()
                contractor_image = Image.open(contractor_stream)
                contractor_image = contractor_image.resize((item["width"], item["height"]), Image.ANTIALIAS)
                contractor_image.save(buff222, "JPEG")
                buff222.seek(2)

                cpy2 = Image.new("RGBA", contractor_image.size, (255, 255, 255, 0))
                width = cpy2.size[0]
                height = cpy2.size[1]

                w_cnt = 0
                while w_cnt < width:
                    h_cnt = 0
                    while h_cnt < height:
                        pixel_data = contractor_image.getpixel((w_cnt, h_cnt))
                        cpy2.putpixel((w_cnt, h_cnt), pixel_data)
                        h_cnt += 1
                    w_cnt += 1

                img.paste(cpy2, (item["x"], item["y"]), cpy2)
                bytes_to_close.append(buff222)
                bytes_to_close.append(contractor_stream)

            elif item["value"] == "rep_signature":
                bucket_name = os.environ.get('BUCKET_NAME',
                    app_identity.get_default_gcs_bucket_name())

                bucket = '/' + bucket_name
                filename = bucket + '/Images/RepSignatures/' + rep.identifier + '.jpg'

                retryParameters = gcs.RetryParams(initial_delay=0.2,
                                                max_delay=5.0,
                                                backoff_factor=2,
                                                max_retry_period=15,
                                                urlfetch_timeout=30)

                gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
                rep_stream = BytesIO(gcs_file.read())
                gcs_file.close()

                buff333 = StringIO.StringIO()
                rep_image = Image.open(rep_stream)
                rep_image = rep_image.resize((item["width"], item["height"]), Image.ANTIALIAS)
                #rep_image = ImageEnhance.Color(rep_image).enhance(0.0)
                rep_image.save(buff333, "JPEG")
                buff333.seek(2)

                cpy3 = Image.new("RGBA", rep_image.size, (255, 255, 255, 0))
                width = cpy3.size[0]
                height = cpy3.size[1]

                w_cnt = 0
                while w_cnt < width:
                    h_cnt = 0
                    while h_cnt < height:
                        pixel_data = rep_image.getpixel((w_cnt, h_cnt))
                        cpy3.putpixel((w_cnt, h_cnt), pixel_data)
                        h_cnt += 1
                    w_cnt += 1

                img.paste(cpy3, (item["x"], item["y"]), cpy3)                    
                bytes_to_close.append(buff333)
                bytes_to_close.append(rep_stream)
                #foo = bar
                #rnirnber@gmail.com
                #yes = no

            if "fx_" in item["value"]:
                if not item["value"] in values_dict.keys():
                    values_dict[item["value"]] = str(Helpers.crunch(item["value"], market_identifier, app_entry, survey_booking, proposal_dict, pricing_structures, funds))

            if not item["value"] in ["system_image", "customer_initials", "customer_signature", "contractor_signature", "contractor_logo", "rep_signature"]:

                if not (item["font_family"] + "_" + str(item["font_size"])) in fonts_dict.keys():
                    fonts_dict[item["font_family"] + "_" + str(item["font_size"])] = ImageFont.truetype(item["font_family"] + ".ttf", item["font_size"])

                phont = fonts_dict[item["font_family"] + "_" + str(item["font_size"])]
                
                height_offset = 0                
                txt = str(values_dict[item["value"]])
                if item["format"] == "currency_dollar":
                    txt = Helpers.currency_format(float(txt))
                elif item["format"] == "currency_no_dollar":
                    txt = Helpers.currency_format(float(txt)).replace("$", "")
                for line in txt.split("\n"):
                    img2 = Image.new("RGBA", (item["width"], item["height"]), (255, 255, 255, 0))
                    draw = ImageDraw.Draw(img2)                
                    draw.text((0, 0), str(line), Helpers.hex_to_rgb_tuple(item["color"]), font=phont)
                    if item["text_align"] == "center":
                        item["x"] += Helpers.get_centered_text_left_offset(phont, txt, item["width"])
                    img.paste(img2, (item["x"], item["y"] + height_offset), img2)
                    height_offset += int(item["font_size"] * 1.5)

        page_buffers.append(StringIO.StringIO())
        img.save(page_buffers[len(page_buffers) - 1], "PDF", resolution=100.0, quality=100.0)

        if not sig_initial_bytes_to_close is None:
            sig_initial_bytes_to_close.close()
        if not cad_stream_to_close is None:
            cad_stream_to_close.close()
        if not cad_buffer_to_close is None:
            cad_buffer_to_close.close()

        cnt += 1
        idx += 1

    out_doc = PdfFileWriter()
    for buff in page_buffers:
        buff.seek(2)
        out_doc.addPage(PdfFileReader(buff, False).getPage(0))

    final_buff = StringIO.StringIO()
    out_doc.write(final_buff)
    filename4 = bucket + '/TempDocs/' + token + "_" + doc.token + ".pdf"

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file4 = gcs.open(
                    filename4,
                    'w',
                    content_type="application/pdf",
                    options={'x-goog-meta-foo': 'foo',
                             'x-goog-meta-bar': 'bar',
                             'x-goog-acl': 'public-read'},
                    retry_params=write_retry_params)

    gcs_file4.write(final_buff.getvalue())
    gcs_file4.close()
    final_buff.close()
    for item in page_buffers + img_bytes + bytes_to_close:
        item.close()

    if not roof_stream is None:
        roof_stream.close()
    if not buff2224 is None:
        buff2224.close()


    #from google.appengine.api import taskqueue
    #taskqueue.add(url="/tq/mail_signed_docs", params={"token": token, "identifier": app_entry.identifier})
