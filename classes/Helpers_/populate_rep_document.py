@staticmethod
def populate_rep_document(sig, doc, token, pending_user):

    import StringIO
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO

    from fpdf import FPDF
    from PyPDF2 import PdfFileWriter,PdfFileReader

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
    identification_exp_vals = ["1970", "01", "01"]

    authority_text = ""
    if len(stripped_ein) == 0:
        stripped_ein = "            "

    pricing_structures = Helpers.get_pricing_structures()
    funds = Helpers.list_funds()

    ol = OfficeLocation.first(OfficeLocation.identifier == pending_user["user_office"])
    m_identifier = "-1"
    m_name = "---"
    if not ol is None:
        m_identifier = ol.parent_identifier
        parent = OfficeLocation.first(OfficeLocation.identifier == m_identifier)
        if not parent is None:
            m_name = parent.name

    tier_a_comm = float(0)
    if m_identifier in pricing_structures.keys():
        if "baseline_commission" in pricing_structures[m_identifier].keys():
            tier_a_comm = float(pricing_structures[m_identifier]["baseline_commission"])

    tier_a_comm = str(tier_a_comm)

    line_h_indicator = " "

    single_filing_checkbox = ""
    married_filing_checkbox = ""
    married_single_filing_checkbox = ""


    last_name_differs = ""

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
        "c_corp_checkbox": False,
        "s_corp_checkbox": False,
        "partnership_checkbox": False,
        "trust_estate_checkbox": False,
        "limited_liability_checkbox": False,
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
        "secondary_document_issuing_authority": authority_text,
        "secondary_document_number": " ",
        "secondary_document_expiration": "1970-01-01",
        "recruiter_first_and_last": " ",
        "rep_tier_a_commission": tier_a_comm,
        "new_power_signature": "sig",
        "fx_Market_Name": m_name,
        "user_emergency_name": pending_user["user_emergency_name"],
        "user_emergency_phone": Helpers.format_phone_number(pending_user["user_emergency_phone"])
    }
    if values_dict["business_name"] == "NA":
        values_dict["business_name"] = ""

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
    while cnt <= doc.page_count:
        filename = bucket + "/Images/Docs/" + doc.token + "/300/" + str(cnt) + ".jpg"
        gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)
        img_bytes.append(BytesIO(gcs_file.read()))
        gcs_file.close()
        img = Image.open(img_bytes[idx])

        for item in template_items[idx]:            

            for key in ["width", "height", "x", "y", "font_size"]:
                item[key] = Helpers.adjust_pixel_size(item[key], 612, 2550)

            if item["value"] == "employee_signature":
                bayse64 = sig

                sig_initial_bytes_to_close = BytesIO(base64.b64decode(bayse64))
                img2 = Image.open(sig_initial_bytes_to_close)
                img2 = img2.resize((item["width"], item["height"]), Image.ANTIALIAS)
                img.paste(img2, (item["x"], item["y"]), img2)


            elif item["value"] == "new_power_signature":
                filename = bucket + "/Images/np_sig.jpg"
                gcs_file = gcs.open(filename, 'r', retry_params=retryParameters)


                bytes = BytesIO(gcs_file.read())
                img2 = Image.open(bytes).convert("RGBA")
                img2 = img2.resize((item["width"], item["height"]), Image.ANTIALIAS)

                bytes_to_close.append(bytes)
                img.paste(img2, (item["x"], item["y"]), img2)
                gcs_file.close()
                
            elif item["value"] in ["individual_sole_proprietor_checkbox", "c_corp_checkbox", "s_corp_checkbox", "partnership_checkbox", "trust_estate_checkbox", "limited_liability_checkbox"]:
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

            else:
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
                logging.info(item)
                draw.text((0, 0), txt, Helpers.hex_to_rgb_tuple(item["color"]), font=phont)

                if item["text_align"] == "center":
                    item["x"] += Helpers.get_centered_text_left_offset(phont, values_dict[item["value"]], item["width"])
                img.paste(img2, (item["x"], item["y"]), img2)

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

