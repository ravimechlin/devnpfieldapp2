def get(self, doc_token, idx, app_identifier):
    from PIL import ImageEnhance

    bytes_to_close = []
    import base64
    import json
    rw_item = None

    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == app_identifier)
    kv_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "new_user_registration_" + app_identifier)
    if not app_entry is None:
        proposal = CustomerProposalInfo.first(CustomerProposalInfo.field_app_identifier == app_identifier)
        if proposal is None:
            proposal = CustomerProposalInfo(
                identifier=Helpers.guid(),
                field_app_identifier=app_identifier,
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


        booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
        if booking is None:
            return
        
        is_cash = ("cash" in booking.fund)
        is_financed = (not is_cash)

        step = int(self.request.get("step"))
        from PIL import Image, ImageDraw, ImageFont
        import StringIO
        from io import BytesIO

        market_identifier = "-1"
        ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
        if not ol is None:
            market_identifier = ol.parent_identifier

        doc = ComposedDocument.first(ComposedDocument.token == doc_token)
        if not doc is None:
            proposal.fix_system_size()
            #fix_additional_amount(proposal)#
            proposal.fix_additional_amount()
            proposal_dict = json.loads(proposal.info)

            az = ""
            if "azimuth" in proposal_dict.keys():
                az = proposal_dict["azimuth"]

            esa = ""
            if "estimated_slope_of_array" in proposal_dict.keys():
                esa = proposal_dict["estimated_slope_of_array"]

            add = app_entry.customer_address.split(" ")
            city = app_entry.customer_city.split(" ")
            formatted_add = ""
            formatted_city = ""
            cnt = 0
            for component in add:
                formatted_add += component.strip()
                if not cnt == len(add) - 1:
                    formatted_add += " "
                cnt += 1

            for component in city:
                formatted_city += component.strip() + " "

            formatted_city = formatted_city.strip()

            panel_qty = proposal_dict["panel_qty"]
            if "new_panel_qty" in proposal_dict.keys():
                panel_qty = proposal_dict["new_panel_qty"]

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


            add_svcs = ""
            additional_services = Helpers.read_setting("services_schedule")
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

            rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)            
            funds = Helpers.list_funds()

            values_dict = {
                "customer_signature": "sig",
                "customer_initials": "initials",
                "todays_date": str(Helpers.pacific_today()).replace("-", " / "),
                "three_business_days": str(Helpers.next_business_days(Helpers.pacific_today(), 3)).replace("-", " / "),
                "day_after_NOC": str(four_days).replace("-", " / "),
                "fund_apr": "0.00%",
                "azimuth": az,
                "array_slope": esa,
                "cash_deal": ["", "X"][int(is_cash)],
                "financed_deal": ["", "X"][int(is_financed)],
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
                "utility_account_holder": "---",
                "contractor_signature": "---",
                "contractor_logo": "---",
                "rep_license_number": "999999",
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
                "cosigner_name": "",
                "cosigner_signature": "co_sig",
                "cosigner_initials": "co_initials",
                "rep_phone": "",
                "cs_plan_price": "0.00",
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
            cosigner_exists = (not cs_kv1 is None)
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

            values_dict["batch_id"] = hashlib.md5(Helpers.guid()).hexdigest()
            values_dict["document_id"] = hashlib.md5(Helpers.guid()).hexdigest()

            for fund in funds:
                if fund["value"] == booking.fund:
                    apr = float(fund["apr"])
                    apr *= float(100)
                    apr = round(apr, 2)
                    apr = str(apr)
                    apr = apr + "%"
                    values_dict["fund_apr"] = apr


            tod = values_dict["todays_date"].split(" / ")
            values_dict["todays_date"] = tod[1] + " / " + tod[2] + " / " + tod[0]

            three_days = values_dict["three_business_days"].split("/")
            values_dict["three_business_days"] = three_days[1] + " / " + three_days[2] + " / " + three_days[0]

            four_days = values_dict["day_after_NOC"].split(" / ")
            values_dict["day_after_NOC"] = four_days[1] + " / " + four_days[2] + " / " + four_days[0]

            security_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == app_entry.identifier + "_secret_qa")
            if not security_kv is None:
                security_info = json.loads(security_kv.val)
                values_dict["security_question"] = security_info["question"]
                values_dict["security_answer"] = security_info["answer"]

            values_dict["current_timestamp"] = str(Helpers.pacific_now()).split(".")[0]

            viewed_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "docs_viewed_ts_" + app_entry.identifier)
            if not viewed_kv is None:
                values_dict["docs_viewed_timestamp"] = viewed_kv.val

            docs_gen_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "docs_gen_timestamp_" + app_entry.identifier)
            if not docs_gen_kv is None:
                values_dict["docs_gen_timestamp"] = docs_gen_kv.val

            cost_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "confirmed_roof_work_numbers_" + app_entry.identifier)
            if not cost_kv is None:
                cost_info = json.loads(cost_kv.val)
                values_dict["fund_one_cost"] = cost_info["fund_one_cost"]
                values_dict["fund_two_cost"] = cost_info["fund_two_cost"]

            roof_item = RoofWorkItem.first(RoofWorkItem.field_app_identifier == app_entry.identifier)
            if not roof_item is None:
                roof_info = json.loads(roof_item.info)
                if roof_info["rep_selection_one"] == "solar_area_only":
                    values_dict["solar_area_only_checkbox"] = "X"
                elif roof_info["rep_selection_one"] == "full_reroof":
                    values_dict["full_reroof_checkbox"] = "X"

                values_dict["roofing_exclusions"] = roof_info["exclusions"]
                values_dict["roofing_materials"] = roof_info["material_question"]

                rw_item = roof_item


            vals = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(["credit_card_number_" + app_entry.identifier, "credit_card_expiration_month_" + app_entry.identifier, "credit_card_expiration_year_" + app_entry.identifier, "credit_card_cvv_num_" + app_entry.identifier]))
            for val in vals:
                k = val.keyy.replace("_" + app_entry.identifier, "")
                values_dict[k] = val.val

            if not (values_dict["credit_card_expiration_month"] + values_dict["credit_card_expiration_year"]) == "011970":
                dt = datetime(int(values_dict["credit_card_expiration_year"]), int(values_dict["credit_card_expiration_month"]), 1).date()
                dt_vals = str(dt).split("-")
                values_dict["credit_card_expiration_date"] = dt_vals[1] + " / " + dt_vals[0]

            val2 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "utility_person_" + app_entry.identifier)
            if not val2 is None:
                values_dict["utility_account_holder"] = val2.val

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

            self.response.content_type = "image/jpeg"
            bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
            bucket = '/' + bucket_name
            retryParameters = gcs.RetryParams(initial_delay=0.2,
                                                       max_delay=5.0,
                                                       backoff_factor=2,
                                                       max_retry_period=15,
                                                       urlfetch_timeout=30)


            filename = bucket + '/Images/Docs/' + doc_token + "/72/" + str(int(idx) + 1) + ".jpg"

            fonts_dict = {}

            f = gcs.open(filename, 'r', retry_params=retryParameters)
            img_bytes = BytesIO(f.read())
            img = Image.open(img_bytes)
            f.close()
            items = json.loads(doc.template_items)

            #look at cosigner exits, filter out the cosigner items if no cosigner exists
            filtered_items = []
            for item2 in items[int(idx)]:
                if item2["value"] == "cosigner_initials" or item2["value"] == "cosigner_signature":
                    if cosigner_exists:
                        filtered_items.append(item2)
                    else:
                        #nada
                        x324 = 5
                else:
                    filtered_items.append(item2)

            items[int(idx)]  = filtered_items


            pricing_structures = Helpers.get_pricing_structures()
            funds = Helpers.list_funds()
            market_identifier = "-1"
            ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
            if not ol is None:
                market_identifier = ol.parent_identifier

            for item in items[int(idx)]:
                if item["value"] == "customer_signature" or item["value"] == "customer_initials" or item["value"] == "system_image" or item["value"] == "contractor_signature" or item["value"] == "contractor_logo" or item["value"] == "rep_signature" or item["value"] == "roof_work_photo" or item["value"] == "cosigner_signature" or item["value"] == "cosigner_initials":
                    continue

                if "fx_" in item["value"]:
                    if not item["value"] in values_dict.keys():
                        values_dict[item["value"]] = Helpers.crunch(item["value"], market_identifier, app_entry, booking, proposal_dict, pricing_structures, funds)

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
                

            sig_initial_items = []
            for item in items[int(idx)]:
                if item["value"] in ["customer_signature", "customer_initials", "cosigner_signature", "cosigner_initials"]:
                    sig_initial_items.append(item)

            cnt = 0
            while cnt < len(sig_initial_items):
                item = sig_initial_items[cnt]
                img2 = None
                if cnt == step:
                    img2 = Image.new("RGBA", (item["width"],item["height"]), (227, 231, 72, 100))
                else:
                    kv_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == item["value"] + "_" + app_identifier)
                    if not kv_item is None:
                        bytes = BytesIO(base64.b64decode(kv_item.val))
                        img2 = Image.open(bytes)
                        img2 = img2.resize((item["width"], item["height"]), Image.ANTIALIAS)
                        pixdata = img2.load()

                        for y in xrange(img2.size[1]):
                            for x in xrange(img2.size[0]):
                                if pixdata[x, y] == (0, 0, 0, 0):
                                    pixdata[x, y] = (227, 231, 72, 100)

                        bytes_to_close.append(bytes)

                img.paste(img2, (item["x"], item["y"]), img2)

                if cnt == step:
                    break

                cnt += 1

            for item in items[int(idx)]:
                if item["value"] == "system_image":
                    bucket_name = os.environ.get('BUCKET_NAME',
                                                 app_identity.get_default_gcs_bucket_name())

                    bucket = '/' + bucket_name
                    filename = bucket + '/ProposalBlobs/' + app_entry.identifier + "_cad_photo." + proposal_dict["cad_photo"]["extension"]

                    retryParameters = gcs.RetryParams(initial_delay=0.2,
                        max_delay=5.0,
                        backoff_factor=2,
                        max_retry_period=15,
                        urlfetch_timeout=30)

                    gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
                    cad_stream = BytesIO(gcs_file.read())
                    gcs_file.close()


                    buff22 = StringIO.StringIO()
                    cad_image = Image.open(cad_stream)
                    cad_image = cad_image.resize((item["width"], item["height"]), Image.ANTIALIAS)
                    cad_image.save(buff22, "JPEG")
                    buff22.seek(2)

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
                    bytes_to_close.append(buff22)
                    bytes_to_close.append(cad_stream)

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

                elif item["value"] == "roof_work_photo":
                    img_postfix = "reroof_photo"
                    if not values_dict["full_reroof_checkbox"] == "X":
                        img_postfix = "solar_area_photo"


                    bucket_name = os.environ.get('BUCKET_NAME',
                                                app_identity.get_default_gcs_bucket_name())

                    bucket = '/' + bucket_name
                    filename = bucket + '/Images/RoofWorkDetails/' + app_entry.identifier + "/" + img_postfix + ".jpg"

                    retryParameters = gcs.RetryParams(initial_delay=0.2,
                                                    max_delay=5.0,
                                                    backoff_factor=2,
                                                    max_retry_period=15,
                                                    urlfetch_timeout=30)

                    gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
                    roof_stream = BytesIO(gcs_file.read())
                    gcs_file.close()

                    buff456 = StringIO.StringIO()
                    rep_image_roof_img = Image.open(roof_stream)
                    rep_image_roof_img = rep_image_roof_img.resize((item["width"], item["height"]), Image.ANTIALIAS)
                    #rep_image = ImageEnhance.Color(rep_image).enhance(0.0)
                    rep_image_roof_img.save(buff456, "JPEG")
                    buff456.seek(2)

                    cpy3 = Image.new("RGBA", rep_image_roof_img.size, (255, 255, 255, 0))
                    width = cpy3.size[0]
                    height = cpy3.size[1]

                    w_cnt = 0
                    while w_cnt < width:
                        h_cnt = 0
                        while h_cnt < height:
                            pixel_data = rep_image_roof_img.getpixel((w_cnt, h_cnt))
                            cpy3.putpixel((w_cnt, h_cnt), pixel_data)
                            h_cnt += 1
                        w_cnt += 1

                    img.paste(cpy3, (item["x"], item["y"]), cpy3)                    
                    bytes_to_close.append(buff456)
                    bytes_to_close.append(roof_stream)


            #if not kv_item is None:
                #bytes = BytesIO(base64.b64decode(kv_item.val))
                #img2 = Image.open(bytes)
                #img2 = img2.resize((item["width"], item["height"]), Image.ANTIALIAS)

            #for item in items[int(idx)]:
            #    rgba = (255, 255, 255, 0)
            #    if cnt == step:
            #        rgba = (227, 231, 72, 100)

            #   if cnt == step:
            #        break

            #   if not item["value"] == "customer_signature":
            #        rgba = (255, 255, 255, 0)
            #        if cnt == step - 1:
            #            rgba = (227, 231, 72, 100)

             ##       if not (item["font_family"] + "_" + str(item["font_size"])) in fonts_dict.keys():
              #         fonts_dict[item["font_family"] + "_" + str(item["font_size"])] = ImageFont.truetype(item["font_family"] + ".ttf", item["font_size"])
              #      phont = fonts_dict[item["font_family"] + "_" + str(item["font_size"])]

              #      img2 = Image.new("RGBA", (item["width"],item["height"]), rgba)
              ##      draw = ImageDraw.Draw(img2)
               #     draw.text((0, 0), values_dict[item["value"]], Helpers.hex_to_rgb_tuple(item["color"]), font=phont)
               #     img.paste(img2, (item["x"], item["y"]), img2)
               #     cnt += 1
               # else:
               #     kv_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "customer_signature_" + app_identifier)
               #     if not kv_item is None:
               #         bytes = BytesIO(base64.b64decode(kv_item.val))
               #         img2 = Image.open(bytes)
               #         img2 = img2.resize((item["width"], item["height"]), Image.ANTIALIAS)

                ##        if cnt == step - 1:
                  #          pixdata = img2.load()

                   #         for y in xrange(img2.size[1]):
                    #            for x in xrange(img2.size[0]):
                     #               if pixdata[x, y] == (0, 0, 0, 0):
                      #                  pixdata[x, y] = (227, 231, 72, 100)

    #

      #                  cnt += 1

            output = StringIO.StringIO()
            img.save(output, format="jpeg", quality=100)
            bytes = output.getvalue()
            self.response.out.write(bytes)
            output.close()
            img_bytes.close()
            for item in bytes_to_close:
                item.close()

    elif (not kv_item is None):
        pending_user = json.loads(kv_item.val)

        step = int(self.request.get("step"))
        from PIL import Image, ImageDraw, ImageFont
        import StringIO
        from io import BytesIO

        doc = ComposedDocument.first(ComposedDocument.token == doc_token)
        if not doc is None:

            add = pending_user["user_address"].split(" ")
            city = pending_user["user_city"].split(" ")
            formatted_add = ""
            formatted_city = ""
            cnt = 0
            for component in add:
                formatted_add += component.strip()
                if not cnt == len(add) - 1:
                    formatted_add += " "
                cnt += 1

            for component in city:
                formatted_city += component.strip() + " "

            formatted_city = formatted_city.strip()

            stripped_ss = "0000000000"
            stripped_ein = "00000000000000000000"
            today = str(Helpers.pacific_today())
            today_vals = today.split("-")
            today_str = today_vals[1] + "/" + today_vals[2] + "/" + today_vals[0]
            dob_vals = pending_user["user_dob"].split("-")
            identification_exp_vals = "1970-01-01"

            
            if len(stripped_ein) == 0:
                stripped_ein = "            "

            pricing_structures = Helpers.get_pricing_structures()
            funds = Helpers.list_funds()

            ol = OfficeLocation.first(OfficeLocation.identifier == pending_user["user_office"])
            m_identifier = "-1"
            m_name = ""
            if not ol is None:
                m_identifier = ol.parent_identifier
                par = OfficeLocation.first(OfficeLocation.identifier == m_identifier)
                if not par is None:
                    m_name = par.name

            tier_a_comm = float(0)
            if m_identifier in pricing_structures.keys():
                if "baseline_commission" in pricing_structures[m_identifier].keys():
                    tier_a_comm = float(pricing_structures[m_identifier]["baseline_commission"])

            tier_a_comm = str(tier_a_comm)

            residual_amount = "0"
            off = OfficeLocation.first(OfficeLocation.identifier == pending_user["user_office"])
            if not off is None:
                mkt = OfficeLocation.first(OfficeLocation.identifier == off.parent_identifier)
                pricing_structures = Helpers.get_pricing_structures()
                market_key = mkt.identifier
                if market_key in pricing_structures.keys():
                    if "residual_pay_per_kw" in pricing_structures[market_key].keys():
                        residual_amount = pricing_structures[market_key]["residual_pay_per_kw"].replace("$", "").replace(",", "")

            values_dict = {
                "employee_first_name": pending_user["user_first"].strip().title(),
                "employee_last_name": pending_user["user_last"].strip().title(),
                "employee_middle_name": pending_user["user_middle"].strip().title(),
                "employee_middle_initial": pending_user["user_middle"].upper()[0],
                "employee_first_last": pending_user["user_first"].strip().title() + " " + pending_user["user_last"].strip().title(),
                "business_name": " ",
                "individual_sole_proprietor_checkbox": (False),
                "c_corp_checkbox": (False),
                "s_corp_checkbox": (False),
                "partnership_checkbox": (False),
                "trust_estate_checkbox": (False),
                "limited_liability_checkbox": (False),
                "employee_address": formatted_add,
                "employee_city": formatted_city,
                "employee_state": pending_user["user_state"].upper(),
                "employee_postal": pending_user["user_postal"].upper(),
                "employee_full_address": formatted_add + " " + formatted_city + ", " + pending_user["user_state"].upper() + " " + pending_user["user_postal"],
                "employee_city_state_zip": formatted_city + ", " + pending_user["user_state"].upper() + " " + pending_user["user_postal"],
                "residual_amount": residual_amount,
                "employee_social_security": stripped_ss,
                "employee_social_security_1": stripped_ss[0],
                "employee_social_security_2": stripped_ss[1],
                "employee_social_security_3": stripped_ss[2],
                "employee_social_security_4": stripped_ss[3],
                "employee_social_security_5": stripped_ss[4],
                "employee_social_security_6": stripped_ss[5],
                "employee_social_security_7": stripped_ss[6],
                "employee_social_security_8": stripped_ss[7],
                "employee_social_security_9": stripped_ss[8],
                "employee_ein": stripped_ein,
                "employee_ein_digital_1": stripped_ein[0],
                "employee_ein_digital_2": stripped_ein[1],
                "employee_ein_digital_3": stripped_ein[2],
                "employee_ein_digital_4": stripped_ein[3],
                "employee_ein_digital_5": stripped_ein[4],
                "employee_ein_digital_6": stripped_ein[5],
                "employee_ein_digital_7": stripped_ein[6],
                "employee_ein_digital_8": stripped_ein[7],
                "employee_ein_digital_9": stripped_ein[8],
                "w2_line_A_indicator": " ",
                "w2_line_B_indicator": " ",
                "w2_line_C_indicator": " ",
                "w2_line_D_indicator": " ",
                "w2_line_E_indicator": " ",
                "w2_line_F_indicator": " ",
                "w2_line_G_indicator": " ",
                "w2_line_H_indicator": " ",
                "w2_file_single_checkbox": " ",
                "w2_file_married_checkbox": " ",
                "w2_file_single_married_checkbox": " ",
                "w2_last_name_differs_checkbox": " ",
                "w2_additional_witholding_amount": " ",
                "employee_signature": "sig",
                "employee_direct_deposit_name": " ",
                "employee_direct_deposit_bank_name": " ",
                "employee_direct_deposit_account_number": " ",
                "employee_direct_deposit_routing_number": " ",
                "employee_direct_deposit_account_type": " ",
                "todays_date": today_str,
                "employee_dob": dob_vals[0] + "/" + dob_vals[1] + "/" + dob_vals[2],
                "employee_email": pending_user["user_email"],
                "employee_phone": Helpers.format_phone_number(Helpers.numbers_from_str(pending_user["user_phone"])),
                "secondary_document_title": " ",
                "secondary_document_issuing_authority": " ",
                "secondary_document_number": " ",
                "secondary_document_expiration": " ",
                "recruiter_first_and_last": "  ",
                "rep_tier_a_commission": tier_a_comm,
                "new_power_signature": "sig",
                "fx_Market_Name": m_name,
                "user_emergency_name": pending_user["user_emergency_name"],
                "user_emergency_phone": Helpers.format_phone_number(pending_user["user_emergency_phone"])
            }
            for num in [1, 2, 3, 4, 5, 6, 7, 8]:
                values_dict["prior_work_title_" + str(num)] = pending_user["prior_work_title_" + str(num)]
                values_dict["prior_work_date_" + str(num)] = pending_user["prior_work_date_" + str(num)]
                values_dict["prior_work_description_" + str(num)] = pending_user["prior_work_description_" + str(num)]

            def trim(string):
                return string.strip()

            prior_work_num_items = 0
            for num in [1, 2, 3, 4, 5, 6, 7, 8]:
                trimmed1 = trim(pending_user["prior_work_title_" + str(num)])
                trimmed2 = trim(pending_user["prior_work_date_" + str(num)])
                trimmed3 = trim(pending_user["prior_work_description_" + str(num)])
                blank = ((len(trimmed1) == 0) and (len(trimmed2) == 0) and (len(trimmed2) == 0))
                if blank:
                    prior_work_num_items = num - 1
                    break

            values_dict["prior_work_num_items"] = str(prior_work_num_items)

            if values_dict["business_name"] == "NA":
                values_dict["business_name"] = ""


            self.response.content_type = "image/jpeg"
            bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
            bucket = '/' + bucket_name
            retryParameters = gcs.RetryParams(initial_delay=0.2,
                                                       max_delay=5.0,
                                                       backoff_factor=2,
                                                       max_retry_period=15,
                                                       urlfetch_timeout=30)


            filename = bucket + '/Images/Docs/' + doc_token + "/72/" + str(int(idx) + 1) + ".jpg"

            fonts_dict = {}

            f = gcs.open(filename, 'r', retry_params=retryParameters)
            img_bytes = BytesIO(f.read())
            img = Image.open(img_bytes)
            f.close()
            items = json.loads(doc.template_items)
            for item in items[int(idx)]:
                if item["value"] == "employee_signature" or item["value"] == "new_power_signature" or item["value"] in ["individual_sole_proprietor_checkbox", "c_corp_checkbox", "s_corp_checkbox", "partnership_checkbox", "trust_estate_checkbox", "limited_liability_checkbox"]:
                    continue


                if not (item["font_family"] + "_" + str(item["font_size"])) in fonts_dict.keys():
                    fonts_dict[item["font_family"] + "_" + str(item["font_size"])] = ImageFont.truetype(item["font_family"] + ".ttf", item["font_size"])

                phont = fonts_dict[item["font_family"] + "_" + str(item["font_size"])]

                img2 = Image.new("RGBA", (item["width"], item["height"]), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img2)
                txt = values_dict[item["value"]]
                if item["format"] == "currency_dollar":
                    txt = Helpers.currency_format(float(txt))
                elif item["format"] == "currency_no_dollar":
                    txt = Helpers.currency_format(float(txt)).replace("$", "")
                draw.text((0, 0), txt, Helpers.hex_to_rgb_tuple(item["color"]), font=phont)

                if item["text_align"] == "center":
                    item["x"] += Helpers.get_centered_text_left_offset(phont, values_dict[item["value"]], item["width"])
                img.paste(img2, (item["x"], item["y"]), img2)

            for item in items[int(idx)]:
                if item["value"] in ["individual_sole_proprietor_checkbox", "c_corp_checkbox", "s_corp_checkbox", "partnership_checkbox", "trust_estate_checkbox", "limited_liability_checkbox"]:
                    bucket_name = os.environ.get('BUCKET_NAME',
                                                 app_identity.get_default_gcs_bucket_name())

                    bucket = '/' + bucket_name
                    filename = bucket + '/Images/filled_' + str(int(values_dict[item["value"]])) + ".jpg"

                    retryParameters = gcs.RetryParams(initial_delay=0.2,
                        max_delay=5.0,
                        backoff_factor=2,
                        max_retry_period=15,
                        urlfetch_timeout=30)

                    gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
                    cad_stream = BytesIO(gcs_file.read())
                    gcs_file.close()


                    buff22 = StringIO.StringIO()
                    cad_image = Image.open(cad_stream)
                    cad_image = cad_image.resize((item["width"], item["height"]), Image.ANTIALIAS)
                    cad_image.save(buff22, "JPEG")
                    buff22.seek(2)

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
                    bytes_to_close.append(buff22)
                    bytes_to_close.append(cad_stream)

            sig_initial_items = []
            np_sig_items = []
            for item in items[int(idx)]:
                if item["value"] == "employee_signature":
                    sig_initial_items.append(item)
                if item["value"] == "new_power_signature":
                    np_sig_items.append(item)

            cnt = 0
            while cnt < len(sig_initial_items):
                item = sig_initial_items[cnt]
                img2 = None
                if cnt == step:
                    img2 = Image.new("RGBA", (item["width"],item["height"]), (227, 231, 72, 100))
                else:
                    kv_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pending_user_signature_" + pending_user["identifier"])
                    if not kv_item is None:
                        bytes = BytesIO(base64.b64decode(kv_item.val))
                        img2 = Image.open(bytes)
                        img2 = img2.resize((item["width"], item["height"]), Image.ANTIALIAS)
                        pixdata = img2.load()

                        for y in xrange(img2.size[1]):
                            for x in xrange(img2.size[0]):
                                if pixdata[x, y] == (0, 0, 0, 0):
                                    pixdata[x, y] = (227, 231, 72, 100)

                        bytes_to_close.append(bytes)

                img.paste(img2, (item["x"], item["y"]), img2)

                if cnt == step:
                    break

                cnt += 1

            cnt = 0
            while cnt < len(np_sig_items):
                item = np_sig_items[cnt]
                img2 = None
                retryParameters = gcs.RetryParams(initial_delay=0.2,
                                               max_delay=5.0,
                                               backoff_factor=2,
                                               max_retry_period=15,
                                               urlfetch_timeout=30)
                bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
                bucket = '/' + bucket_name
                filename = bucket + "/Images/np_sig.jpg"
                gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)


                bytes = BytesIO(gcs_file.read())
                img2 = Image.open(bytes).convert("RGBA")
                img2 = img2.resize((item["width"], item["height"]), Image.ANTIALIAS)
                pixdata = img2.load()

                bytes_to_close.append(bytes)
                img.paste(img2, (item["x"], item["y"]), img2)
                gcs_file.close()
                cnt += 1

            output = StringIO.StringIO()
            nine = 9
            img.save(output, format="jpeg", quality=100)
            bytes = output.getvalue()
            self.response.out.write(bytes)
            output.close()
            img_bytes.close()
            for item in bytes_to_close:
                item.close()

