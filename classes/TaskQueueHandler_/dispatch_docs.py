def dispatch_docs(self):
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    from google.appengine.api import taskqueue
    token = hashlib.md5(Helpers.guid()).hexdigest()
    

    docs_info = {"greensky": lambda app_entry, booking, proposal: booking.fund == "ca_greensky",
                    "ut_greensky": lambda app_entry, booking, proposal: booking.fund in ["ut_greensky", "ut_twelve_greensky"],
                    "hero": lambda app_entry, booking, proposal: booking.fund == "hero" and app_entry.customer_county in ["Riverside County", "Imperial County", "San Diego County", "San Bernardino County", "Orange County"],
                    "kw": lambda app_entry, booking, proposal: (booking.fund == "kw" and app_entry.customer_state == "CA") or (booking.fund == "hero" and app_entry.customer_county in ["Los Angeles County", "Ventura County"]),
                    "rmp": lambda app_entry, booking, proposal: booking.fund == "ut_kw_product",
                    "incentive_ca": lambda app_entry, booking, proposal: app_entry.customer_state == "CA",
                    "incentive_ut": lambda app_entry, booking, proposal: app_entry.customer_state == "UT",
                    "sce": lambda app_entry, booking, proposal: app_entry.utility_provider == "southern_california_edison",
                    "sdge": lambda app_entry, booking, proposal: app_entry.utility_provider == "san_diego_gas_&_electric",
                    "corona_carbon": lambda app_entry, booking, proposal: (int(app_entry.customer_postal) >= 92877 and int(app_entry.customer_postal) <= 92883) or (app_entry.customer_city.strip().lower() == "corona" and app_entry.customer_county == "Riverside County"),
                    "la_county": lambda app_entry, booking, proposal: app_entry.customer_county == "Los Angeles County",
                    "apple_valley_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal == "92307" or app_entry.customer_postal == "92308",
                    "chino_hills_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal == "91709",
                    "rancho_santa_margarita_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal == "92688",
                    "desert_hot_springs_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal == "92240" or app_entry.customer_postal == "92241",
                    "eastvale_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal == "91752" or app_entry.customer_postal == "92880",
                    "jurupa_valley_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92509", "91752"],
                    "laguna_hills_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92653", "92654"],
                    "lake_forest_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal == "92630",
                    "long_beach_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["90731", "90755", "90802", "90803", "90804", "90806", "90808", "90813", "90814", "90815", "90822", "90831"],
                    "mission_viejo_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92690", "92691", "92692"],
                    "moreno_valley_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92551", "92552", "92553", "92554", "92555", "92556", "92557"],
                    "orange_county_carbon": lambda app_entry, booking, proposal: app_entry.customer_county == "Orange County",
                    "palm_desert_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92211", "92255", "92260", "92261"],
                    "perris_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92570", "92571", "92572", "92599"],
                    "redlands_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92373", "92374", "92375"],
                    "rialto_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92376", "92377"],
                    "riverside_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92501", "92502", "92503", "92504", "92505", "92507", "92508", "92509", "92513", "92514", "92515", "92516", "92517", "92519", "92521", "92522"],
                    "san_bernardino_carbon": lambda app_entry, booking, proposal: app_entry.customer_county == "San Bernardino County",
                    "santa_ana_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92701", "92702", "92703", "92704", "92705", "92706", "92707", "92711", "92712", "92725", "92735", "92799"],
                    "victorville_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal in ["92392", "92393", "92394", "92395"],
                    "wildomar_carbon": lambda app_entry, booking, proposal: app_entry.customer_postal == "92595"
                }
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("identifier"))
    if not app_entry is None:
        booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
        if not booking is None:
            proposal = CustomerProposalInfo.first(CustomerProposalInfo.field_app_identifier == self.request.get("identifier"))
            if not proposal is None:
                proposal.fix_additional_amount()
                rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
                if not rep is None:
                    doc_idx = 0
                    existing_idxes = []
                    while doc_idx <= (len(docs_info.keys()) - 1):
                        key = docs_info.keys()[doc_idx]
                        if docs_info[key](app_entry, booking, proposal):
                            existing_idxes.append(doc_idx)

                            if str(self.request.get("is_greensky")) == "1":
                                Helpers.populate_document(key, app_entry, booking, proposal, token, doc_idx, rep, True, self.request.get("incentive"), self.request.get("utility_person"), self.request.get("acct_num"), self.request.get("exp_year"), self.request.get("exp_month"), self.request.get("cvv"))
                            else:
                                Helpers.populate_document(key, app_entry, booking, proposal, token, doc_idx, rep, True, self.request.get("incentive"), self.request.get("utility_person"))

                        doc_idx += 1

                    #generate the system layout
                    proposal_dict = json.loads(proposal.info)
                    proposal_keys = proposal_dict.keys()

                    if "panel_type" in proposal_dict.keys() and "new_panel_qty" in proposal_dict.keys() and "panel_qty_override" in proposal_dict.keys():
                        if "[[[" in proposal_dict["panel_type"]:
                            wattage = proposal_dict["panel_type"][proposal_dict["panel_type"].index("[[["):]
                            wattage = wattage.replace("[[[", "").replace("]]]", "")
                            wattage = float(wattage)

                            new_ss = wattage * float(proposal_dict["new_panel_qty"])
                            new_ss /= float(1000)
                            proposal_dict["system_size"] = str(new_ss)

                    if "panel_type" in proposal_keys and "panel_qty" in proposal_keys and "inverter_type" in proposal_keys and "inverter_qty" in proposal_keys and "racking" in proposal_keys:
                        if "[[[" in proposal_dict["panel_type"]:
                            proposal_dict["panel_type"] = proposal_dict["panel_type"][0:proposal_dict["panel_type"].index("[[[")]
                        existing_idxes = [99] + existing_idxes

                        panel_qty = proposal_dict["panel_qty"]
                        if "new_panel_qty" in proposal_keys:
                            panel_qty = proposal_dict["new_panel_qty"]
                        font1 = ImageFont.truetype("Lato-Light.ttf", 48)
                        font2 = ImageFont.truetype("DROIDSANS-BOLD.ttf", 72)
                        font3 = ImageFont.truetype("Lato-Medium.ttf", 58)
                        font4 = ImageFont.truetype("DROIDSANS-BOLD.ttf", 58)
                        font5 = ImageFont.truetype("DROIDSANS-BOLD.ttf", 36)

                        layout_bytes = BytesIO(base64.b64decode(Helpers.get_pdf_image("system_layout_" + app_entry.customer_state)))
                        layout_img = Image.open(layout_bytes)

                        customer_name_image = Image.new("RGBA", (900, 300), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(customer_name_image)
                        draw.text((5, 0), app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(), (92, 105, 112), font=font1)
                        l_off = Helpers.get_centered_text_left_offset(font1, app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(), 660)
                        layout_img.paste(customer_name_image, (230 + l_off, 1010), customer_name_image)

                        add_components = app_entry.customer_address.split(" ")
                        cnt = 0
                        for add in add_components:
                            add_components[cnt] = add.strip().title()
                            cnt += 1
                        add_txt = " ".join(add_components)
                        address_image = Image.new("RGBA", (900, 300), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(address_image)
                        draw.text((5, 0), add_txt, (92, 105, 112), font=font1)
                        l_off = Helpers.get_centered_text_left_offset(font1, add_txt, 660)
                        layout_img.paste(address_image, (230 + l_off, 1070), address_image)

                        city_state_zip_txt = app_entry.customer_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal
                        city_state_zip_image = Image.new("RGBA", (900, 300), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(city_state_zip_image)
                        draw.text((5, 0), city_state_zip_txt, (92, 105, 112), font=font1)
                        l_off = Helpers.get_centered_text_left_offset(font1, city_state_zip_txt, 660)
                        layout_img.paste(city_state_zip_image, (230 + l_off, 1130), city_state_zip_image)

                        sys_size_image = Image.new("RGBA", (900, 300), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(sys_size_image)
                        draw.text((5, 0), proposal_dict["system_size"], (247, 150, 33), font=font2)
                        l_off = Helpers.get_centered_text_left_offset(font2, proposal_dict["system_size"], 310)
                        layout_img.paste(sys_size_image, (410 + l_off, 1460), sys_size_image)

                        module_image = Image.new("RGBA", (900, 300), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(module_image)
                        draw.text((5, 0), proposal_dict["panel_type"], (247, 150, 33), font=font3)
                        layout_img.paste(module_image, (980, 1975), module_image)

                        module_qty_image = Image.new("RGBA", (900, 300), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(module_qty_image)
                        draw.text((5, 0), panel_qty, (247, 150, 33), font=font4)
                        l_off = Helpers.get_centered_text_left_offset(font4, panel_qty, 290)
                        layout_img.paste(module_qty_image, (2020 + l_off, 1975), module_qty_image)

                        inverter_image = Image.new("RGBA", (900, 300), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(inverter_image)
                        draw.text((5, 0), proposal_dict["inverter_type"], (247, 150, 33), font=font3)
                        layout_img.paste(inverter_image, (980, 2105), inverter_image)

                        inverter_qty_image = Image.new("RGBA", (900, 300), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(inverter_qty_image)
                        draw.text((5, 0), panel_qty, (247, 150, 33), font=font4)
                        l_off = Helpers.get_centered_text_left_offset(font4, panel_qty, 290)
                        layout_img.paste(inverter_qty_image, (2020 + l_off, 2105), inverter_qty_image)

                        racking_image = Image.new("RGBA", (900, 300), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(racking_image)
                        draw.text((5, 0), proposal_dict["racking"], (247, 150, 33), font=font3)
                        layout_img.paste(racking_image, (980, 2235), racking_image)

                        if not panel_qty == proposal_dict["panel_qty"]:
                            change_image = Image.new("RGBA", (1800, 300), (255, 255, 255, 0))
                            draw = ImageDraw.Draw(change_image)
                            diff = str(int(proposal_dict["panel_qty"]) - int(panel_qty))
                            ptxt = "panel"
                            if int(diff) > 1:
                                ptxt += "s"
                            draw.text((5, 0), "(Your system size has been changed from the actual design shown.", (23, 138, 195), font=font5)
                            layout_img.paste(change_image, (1028, 1720), change_image)

                            change_image2 = Image.new("RGBA", (1800, 300), (255, 255, 255, 0))
                            draw = ImageDraw.Draw(change_image2)
                            draw.text((5, 0), "The design shown has " + diff + " more " + ptxt + " than your system will actually have.)", (23, 138, 195), font=font5)
                            layout_img.paste(change_image2, (1028, 1766), change_image2)

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
                        cad_image = cad_image.resize((1322, 991), Image.ANTIALIAS)
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

                        layout_img.paste(cpy, (1020, 720), cpy)

                        buff4 = StringIO.StringIO()
                        layout_img.save(buff4, "PDF", resolution=100.0, quality=100.0)
                        buff4.seek(2)

                        filename = bucket + '/TempDocs/' + token + "_99.pdf"
                        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
                        gcs_file3 = gcs.open(
                                        filename,
                                        'w',
                                        content_type="application/pdf",
                                        options={'x-goog-meta-foo': 'foo',
                                                    'x-goog-meta-bar': 'bar',
                                                    'x-goog-acl': 'public-read'},
                                        retry_params=write_retry_params)
                        gcs_file3.write(buff4.getvalue())
                        gcs_file3.close()

                        layout_bytes.close()
                        buff4.close()
                        buff22.close()
                        cad_stream.close()

                    taskqueue.add(url="/tq/send_docs", params={"token": token, "idxs": json.dumps(existing_idxes), "rep_email": rep.rep_email, "customer_name": booking.name.strip().replace(" ", "_")})
