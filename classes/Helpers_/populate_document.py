@staticmethod
def populate_document(doc_name, app_entry, survey_booking, proposal, token, doc_idx, rep=None, write_to_gcs=False, incentive=None, utility_person=None, acct_num="", exp_year="", exp_month="", cvv=""):
    exp_date_str = ""
    if (not exp_year == "") and (not exp_month == ""):
        exp_date = datetime(int(exp_year), int(exp_month), 1)
        exp_date_str = str(exp_date).split("-")[0] + "/" + str(exp_date).split("-")[1]
    if utility_person is None:
        utility_person = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()

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

    doc_page_count_dict = {"greensky": 6, "ut_greensky": 8, "hero": 5, "kw": 5, "rmp": 7, "incentive_ca": 3, "incentive_ut": 3, "sce": 2, "sdge": 3, "corona_carbon": 1, "la_county": 2, "apple_valley_carbon": 1, "chino_hills_carbon": 1, "rancho_santa_margarita_carbon": 1, "desert_hot_springs_carbon": 1, "eastvale_carbon": 1, "jurupa_valley_carbon": 1, "laguna_hills_carbon": 1, "lake_forest_carbon": 2, "long_beach_carbon": 1, "mission_viejo_carbon": 1, "moreno_valley_carbon": 1, "orange_county_carbon": 1, "palm_desert_carbon": 1, "perris_carbon": 1, "redlands_carbon": 1, "rialto_carbon": 2, "riverside_carbon": 2, "san_bernardino_carbon": 1, "santa_ana_carbon": 1, "victorville_carbon": 1, "wildomar_carbon": 1}

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

    today_vals = str(Helpers.pacific_today()).split("-")
    today_str = today_vals[1] + "/" + today_vals[2] + "/" + today_vals[0]

    three_days_later_vals = str(Helpers.next_business_days(Helpers.pacific_now(), 3)).split("-")
    three_days_later_str = three_days_later_vals[1] + "/" + three_days_later_vals[2] + "/" + three_days_later_vals[0]

    kv_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "NOC_" + app_entry.identifier)
    if kv_item is None:
        kv_item = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="NOC_" + app_entry.identifier,
            expiration=Helpers.pacific_now() + timedelta(days=180)
        )
    kv_item.val = three_days_later_str
    kv_item.put()

    info = json.loads(proposal.info)
    if "panel_type" in info.keys() and "new_panel_qty" in info.keys() and "panel_qty_override" in info.keys():
        if "[[[" in info["panel_type"]:
            wattage = info["panel_type"][info["panel_type"].index("[[["):]
            wattage = wattage.replace("[[[", "").replace("]]]", "")
            wattage = float(wattage)

            new_ss = wattage * float(info["new_panel_qty"])
            new_ss /= float(1000)
            info["system_size"] = str(new_ss)

    system_cost_formula = Helpers.compile_formula("fx_Total_System_Cost")
    if not system_cost_formula is None:
        sys_cost = system_cost_formula["fn"](app_entry, survey_booking, info)
        greensky_down = sys_cost * 0.1
        thirty_percent = sys_cost * 0.3
        seventy_percent = sys_cost * 0.7
        if greensky_down > 1000:
            greensky_down = float(1000)

        #actually it's $0 for greensky
        greensky_down = 0.0

        paste_data = {
            "greensky":
                [
                    [
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_first_name.strip(),
                            "x": 175,
                            "y": 930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_last_name.strip(),
                            "x": 1275,
                            "y": 930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.format_phone_number(app_entry.customer_phone),
                            "x": 175,
                            "y": 1030,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_add,
                            "x": 175,
                            "y": 1130,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_city,
                            "x": 175,
                            "y": 1230,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_postal,
                            "x": 2000,
                            "y": 1230,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(sys_cost).replace("$", ""),
                            "x": 460,
                            "y": 1740,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(greensky_down).replace("$", ""),
                            "x": 1560,
                            "y": 1740,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 36,
                            "text": Helpers.currency_format(greensky_down).replace("$", ""),
                            "x": 2120,
                            "y": 2890,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 36,
                            "text": Helpers.currency_format(sys_cost - greensky_down).replace("$", ""),
                            "x": 2120,
                            "y": 2980,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1580,
                            "y": 2330,
                            "name": "check.jpg"
                        }
                    ],
                    [

                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 64,
                            "text": today_str,
                            "x": 450,
                            "y": 2930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 64,
                            "text": today_str,
                            "x": 1850,
                            "y": 2930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1475,
                            "y": 2735,
                            "name": "check.jpg"
                        },
                        {
                            "type": "image",
                            "x": 2410,
                            "y": 2600,
                            "name": "check.jpg"
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 64,
                            "text": today_str,
                            "x": 675,
                            "y": 1605,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1060,
                            "y": 1630,
                            "name": "check.jpg"
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 72,
                            "text": today_str,
                            "x": 1075,
                            "y": 950,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 36,
                            "text": three_days_later_str,
                            "x": 300,
                            "y": 2090,
                            "rgb": (0, 0, 0)
                        },
                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                            "x": 650,
                            "y": 580,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_add,
                            "x": 400,
                            "y": 705,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_city,
                            "x": 1250,
                            "y": 705,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_postal,
                            "x": 2120,
                            "y": 705,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 48,
                            "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                            "x": 680,
                            "y": 2905,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(sys_cost * 0.20).replace("$", ""),
                            "x": 775,
                            "y": 1375,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": three_days_later_str,
                            "x": 1305,
                            "y": 1375,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(sys_cost * 0.80).replace("$", ""),
                            "x": 775,
                            "y": 1480,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": today_str,
                            "x": 2100,
                            "y": 580,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": acct_num,
                            "x": 715,
                            "y": 1070,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": exp_date_str,
                            "x": 1680,
                            "y": 1070,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": cvv,
                            "x": 2200,
                            "y": 1070,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1525,
                            "y": 2900,
                            "name": "check.jpg"
                        },
                        {
                            "type": "image",
                            "x": 2400,
                            "y": 1400,
                            "name": "check.jpg"
                        }
                    ]
                ],
            "ut_greensky":
                [
                    [
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_first_name.strip().title(),
                            "x": 175,
                            "y": 1060,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 1275,
                            "text": app_entry.customer_last_name.strip().title(),
                            "x": 175,
                            "y": 1060,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.format_phone_number(app_entry.customer_phone),
                            "x": 175,
                            "y": 1170,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_email,
                            "x": 1275,
                            "y": 1170,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_add,
                            "x": 175,
                            "y": 1270,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_city,
                            "x": 175,
                            "y": 1370,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_state,
                            "x": 1275,
                            "y": 1370,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_postal,
                            "x": 2000,
                            "y": 1370,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(sys_cost).replace("$", ""),
                            "x": 500,
                            "y": 1670,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(thirty_percent).replace("$", ""),
                            "x": 1560,
                            "y": 1670,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(thirty_percent).replace("$", ""),
                            "x": 2120,
                            "y": 2640,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(seventy_percent).replace("$", ""),
                            "x": 2120,
                            "y": 2760,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1588,
                            "y": 2084,
                            "name": "check.jpg"
                        }
                    ],
                    [

                    ],
                    [
                        {
                            "type": "image",
                            "x": 1255,
                            "y": 750,
                            "name": "check.jpg"
                        },
                        {
                            "type": "image",
                            "x": 1250,
                            "y": 1840,
                            "name": "check.jpg"
                        },
                        {
                            "type": "image",
                            "x": 2424,
                            "y": 2360,
                            "name": "check.jpg"
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": str(Helpers.pacific_today()),
                            "x": 416,
                            "y": 2535,
                            "rgb": (0, 0, 0)
                        },
                        {
                           "type": "text",
                            "font-size": 58,
                            "text": str(Helpers.pacific_today()),
                            "x": 1840,
                            "y": 2535,
                            "rgb": (0, 0, 0)
                        }
                    ],
                    [
                        {
                           "type": "text",
                            "font-size": 58,
                            "text": str(Helpers.pacific_today()),
                            "x": 635,
                            "y": 1620,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1965,
                            "y": 1642,
                            "name": "check.jpg"
                        }
                    ],
                    [
                        {
                          "type": "text",
                          "font-size": 48,
                          "text": today_str,
                          "x": 1160,
                          "y": 983,
                          "rgb": (0, 0, 0)
                        },
                        {
                          "type": "text",
                          "font-size": 48,
                          "text": three_days_later_str,
                          "x": 180,
                          "y": 2085,
                          "rgb": (0, 0, 0)
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 48,
                            "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                            "x": 670,
                            "y": 1795,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 48,
                            "text": today_str,
                            "x": 670,
                            "y": 2030,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 418,
                            "y": 1670,
                            "name": "check.jpg"
                        }
                    ],
                    [
                        {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                          "x": 730,
                          "y": 1230,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": formatted_add,
                          "x": 730,
                          "y": 1310,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": formatted_city,
                          "x": 460,
                          "y": 1400,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_state,
                          "x": 1480,
                          "y": 1400,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_postal,
                          "x": 1920,
                          "y": 1400,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": "X",
                          "x": 625,
                          "y": 1905,
                          "rgb": (0, 0, 0)
                      }
                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                            "x": 650,
                            "y": 580,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_add,
                            "x": 400,
                            "y": 705,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_city,
                            "x": 1250,
                            "y": 705,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_postal,
                            "x": 2120,
                            "y": 705,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 48,
                            "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                            "x": 680,
                            "y": 2905,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(sys_cost * 0.30).replace("$", ""),
                            "x": 775,
                            "y": 1375,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": three_days_later_str,
                            "x": 1305,
                            "y": 1375,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(sys_cost * 0.70).replace("$", ""),
                            "x": 775,
                            "y": 1480,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": today_str,
                            "x": 2100,
                            "y": 580,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": acct_num,
                            "x": 715,
                            "y": 1070,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": exp_date_str,
                            "x": 1680,
                            "y": 1070,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": cvv,
                            "x": 2200,
                            "y": 1070,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1525,
                            "y": 2900,
                            "name": "check.jpg"
                        },
                        {
                            "type": "image",
                            "x": 2400,
                            "y": 1400,
                            "name": "check.jpg"
                        }
                    ]
                ],
            "hero":
                [
                    [
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_first_name.strip().title(),
                            "x": 180,
                            "y": 930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_last_name.strip().title(),
                            "x": 1260,
                            "y": 930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.format_phone_number(app_entry.customer_phone),
                            "x": 180,
                            "y": 1040,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_add,
                            "x": 180,
                            "y": 1140,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_city,
                            "x": 180,
                            "y": 1240,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_postal,
                            "x": 2000,
                            "y": 1240,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(sys_cost).replace("$", ""),
                            "x": 475,
                            "y": 1725,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(greensky_down).replace("$", ""),
                            "x": 1550,
                            "y": 1725,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 36,
                            "text": Helpers.currency_format(greensky_down).replace("$", ""),
                            "x": 2120,
                            "y": 2890,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 36,
                            "text": Helpers.currency_format(sys_cost - greensky_down).replace("$", ""),
                            "x": 2120,
                            "y": 2980,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1580,
                            "y": 2330,
                            "name": "check.jpg"
                        }
                    ],
                    [

                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 64,
                            "text": today_str,
                            "x": 450,
                            "y": 2930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 64,
                            "text": today_str,
                            "x": 1850,
                            "y": 2930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1475,
                            "y": 2735,
                            "name": "check.jpg"
                        },
                        {
                            "type": "image",
                            "x": 2410,
                            "y": 2600,
                            "name": "check.jpg"
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 64,
                            "text": today_str,
                            "x": 675,
                            "y": 1605,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1060,
                            "y": 1630,
                            "name": "check.jpg"
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 72,
                            "text": today_str,
                            "x": 1075,
                            "y": 950,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 36,
                            "text": three_days_later_str,
                            "x": 300,
                            "y": 2090,
                            "rgb": (0, 0, 0)
                        },
                    ]
                ],
            "kw":
                [
                    [
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_first_name.strip().title(),
                            "x": 160,
                            "y": 930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_last_name.strip().title(),
                            "x": 1270,
                            "y": 930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.format_phone_number(app_entry.customer_phone),
                            "x": 160,
                            "y": 1040,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_add,
                            "x": 160,
                            "y": 1140,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": formatted_city,
                            "x": 160,
                            "y": 1240,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": app_entry.customer_postal,
                            "x": 2200,
                            "y": 1240,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 58,
                            "text": Helpers.currency_format(sys_cost).replace("$", ""),
                            "x": 475,
                            "y": 1725,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 36,
                            "text": Helpers.currency_format(sys_cost).replace("$", ""),
                            "x": 2120,
                            "y": 2980,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1580,
                            "y": 2330,
                            "name": "check.jpg"
                        }
                    ],
                    [
                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 64,
                            "text": today_str,
                            "x": 450,
                            "y": 2930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 64,
                            "text": today_str,
                            "x": 1850,
                            "y": 2930,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1475,
                            "y": 2735,
                            "name": "check.jpg"
                        },
                        {
                            "type": "image",
                            "x": 2410,
                            "y": 2600,
                            "name": "check.jpg"
                        }


                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 64,
                            "text": today_str,
                            "x": 675,
                            "y": 1605,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "image",
                            "x": 1060,
                            "y": 1630,
                            "name": "check.jpg"
                        }
                    ],
                    [
                        {
                            "type": "text",
                            "font-size": 72,
                            "text": today_str,
                            "x": 1075,
                            "y": 950,
                            "rgb": (0, 0, 0)
                        },
                        {
                            "type": "text",
                            "font-size": 36,
                            "text": three_days_later_str,
                            "x": 300,
                            "y": 2090,
                            "rgb": (0, 0, 0)
                        },
                    ]
                ],
            "rmp":
                [
                  [
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_first_name.strip().title(),
                          "x": 750,
                          "y": 500,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_last_name.strip().title(),
                          "x": 1750,
                          "y": 500,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": Helpers.format_phone_number(app_entry.customer_phone),
                          "x": 650,
                          "y": 575,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_email,
                          "x": 650,
                          "y": 650,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": formatted_add,
                          "x": 680,
                          "y": 740,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": formatted_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal,
                          "x": 850,
                          "y": 810,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": Helpers.currency_format(sys_cost).replace("$", ""),
                          "x": 580,
                          "y": 970,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": "0.00",
                          "x": 1730,
                          "y": 970,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": "0.00",
                          "x": 1880,
                          "y": 2470,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": Helpers.currency_format(sys_cost).replace("$", ""),
                          "x": 1880,
                          "y": 2620,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "image",
                          "x": 1609,
                          "y": 1775,
                          "name": "check.jpg"
                      }
                  ],
                  [
                  ],
                  [
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": today_str,
                          "x": 1760,
                          "y": 2875,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "image",
                          "x": 1953,
                          "y": 1014,
                          "name": "check.jpg"
                      },
                      {
                          "type": "image",
                          "x": 1264,
                          "y": 2664,
                          "name": "check.jpg"
                      }
                  ],
                  [
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": today_str,
                          "x": 920,
                          "y": 1830,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "image",
                          "x": 2284,
                          "y": 1829,
                          "name": "check.jpg"
                      }
                  ],
                  [
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": today_str,
                          "x": 350,
                          "y": 580,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": three_days_later_str,
                          "x": 620,
                          "y": 1850,
                          "rgb": (0, 0, 0)
                      }
                  ],
                  [
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                          "x": 670,
                          "y": 1795,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": today_str,
                          "x": 670,
                          "y": 2030,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "image",
                          "x": 418,
                          "y": 1670,
                          "name": "check.jpg"
                      }
                  ],
                  [
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                          "x": 730,
                          "y": 1230,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": formatted_add,
                          "x": 730,
                          "y": 1310,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": formatted_city,
                          "x": 460,
                          "y": 1400,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_state,
                          "x": 1480,
                          "y": 1400,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": app_entry.customer_postal,
                          "x": 1920,
                          "y": 1400,
                          "rgb": (0, 0, 0)
                      },
                      {
                          "type": "text",
                          "font-size": 48,
                          "text": "X",
                          "x": 625,
                          "y": 1905,
                          "rgb": (0, 0, 0)
                      }
                  ]
                ],
            "incentive_ca":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 300,
                        "y": 500,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 1175,
                        "y": 500,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": Helpers.format_phone_number(app_entry.customer_phone),
                        "x": 2025,
                        "y": 500,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 600,
                        "y": 650,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_city,
                        "x": 1400,
                        "y": 650,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_postal,
                        "x": 2225,
                        "y": 650,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": incentive,
                        "x": 280,
                        "y": 890,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 42,
                        "text": today_str,
                        "x": 1175,
                        "y": 2900,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 250,
                        "y": 3050,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": rep.first_name.strip().title() + " " + rep.last_name.strip().title(),
                        "x": 1500,
                        "y": 3050,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": rep.rep_id.upper(),
                        "x": 2175,
                        "y": 3050,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": three_days_later_str,
                        "x": 600,
                        "y": 3800,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 100,
                        "y": 2900,
                        "name": "check.jpg"
                    }
                ],
                [

                ],
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": three_days_later_str,
                        "x": 600,
                        "y": 3750,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "incentive_ut":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 300,
                        "y": 500,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 1175,
                        "y": 500,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": Helpers.format_phone_number(app_entry.customer_phone),
                        "x": 2025,
                        "y": 500,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 600,
                        "y": 650,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_city,
                        "x": 1400,
                        "y": 650,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_postal,
                        "x": 2225,
                        "y": 650,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": incentive,
                        "x": 280,
                        "y": 890,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 42,
                        "text": today_str,
                        "x": 1175,
                        "y": 2900,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 250,
                        "y": 3050,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": rep.first_name.strip().title() + " " + rep.last_name.strip().title(),
                        "x": 1500,
                        "y": 3050,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": rep.rep_id.upper(),
                        "x": 2175,
                        "y": 3050,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": three_days_later_str,
                        "x": 600,
                        "y": 3800,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 100,
                        "y": 2900,
                        "name": "check.jpg"
                    }
                ],
                [

                ],
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": three_days_later_str,
                        "x": 600,
                        "y": 3780,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "sce":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": utility_person,
                        "x": 500,
                        "y": 1265,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 500,
                        "y": 1390,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 385,
                        "y": 1200,
                        "name": "check.jpg"
                    }
                ],
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": utility_person,
                        "x": 500,
                        "y": 1265,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 500,
                        "y": 1390,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 385,
                        "y": 1200,
                        "name": "check.jpg"
                    }
                ]
            ],
            "sdge":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": utility_person,
                        "x": 1150,
                        "y": 700,
                        "rgb": (0, 0, 0)
                    },
                    {
                            "type": "image",
                            "x": 230,
                            "y": 2495,
                            "name": "check.jpg"
                    }
                ],
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": utility_person,
                        "x": 440,
                        "y": 1910,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 365,
                        "y": 1750,
                        "name": "check.jpg"
                    }
                ],
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": utility_person,
                        "x": 900,
                        "y": 1735,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 2025,
                        "y": 1835,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 825,
                        "y": 1840,
                        "name": "check.jpg"
                    }
                ]
            ],
            "corona_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add + " " + formatted_city + ", " + app_entry.customer_state,
                        "x": 775,
                        "y": 2150,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 775,
                        "y": 2375,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1885,
                        "y": 2790,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 760,
                        "y": 2800,
                        "name": "check.jpg"
                    }
                ]
            ],
            "apple_valley_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 560,
                        "y": 1835,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add + " " + formatted_city + ", " + app_entry.customer_state,
                        "x": 560,
                        "y": 1955,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1860,
                        "y": 2096,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 92,
                        "y": 2072,
                        "name": "check.jpg"
                    }
                ]
            ],
            "chino_hills_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 462,
                        "y": 2710,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1524,
                        "y": 2544,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 320,
                        "y": 2542,
                        "name": "check.jpg"
                    }
                ]
            ],
            "rancho_santa_margarita_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 515,
                        "y": 1835,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 515,
                        "y": 2050,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 478,
                        "y": 2254,
                        "name": "check.jpg"
                    }
                ]
            ],
            "desert_hot_springs_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 215,
                        "y": 780,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 1175,
                        "y": 920,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 155,
                        "y": 2330,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 825,
                        "y": 2330,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "eastvale_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 347,
                        "y": 1778,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 347,
                        "y": 1980,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 250,
                        "y": 2185,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1642,
                        "y": 2220,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "jurupa_valley_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 790,
                        "y": 870,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 790,
                        "y": 1090,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1687,
                        "y": 2144,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 632,
                        "y": 2144,
                        "name": "check.jpg"
                    },
                ]
            ],
            "laguna_hills_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 760,
                        "y": 848,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 760,
                        "y": 1060,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1654,
                        "y": 2152,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 602,
                        "y": 2140,
                        "name": "check.jpg"
                    }
                ]
            ],
            "lake_forest_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 761,
                        "y": 494,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 1314,
                        "y": 626,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1846,
                        "y": 2106,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 88,
                        "y": 2488,
                        "name": "check.jpg"
                    }
                ],
                [

                ]
            ],
            "long_beach_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 490,
                        "y": 2578,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1738,
                        "y": 3096,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "mission_viejo_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 800,
                        "y": 710,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 800,
                        "y": 958,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1782,
                        "y": 2092,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 319,
                        "y": 2084,
                        "name": "check.jpg"
                    }
                ]
            ],
            "moreno_valley_carbon":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 265,
                        "y": 746,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 741,
                        "y": 866,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 1731,
                        "y": 2591,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 256,
                        "y": 2600,
                        "name": "check.jpg"
                    }
                ]
            ],
            "orange_county_carbon":
            [
                [
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 48,
                        "x": 660,
                        "y": 920,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 660,
                        "y": 1020,
                        "font-size": 48,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 190,
                        "y": 2530,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": today_str,
                        "x": 1671,
                        "y": 2535,
                        "font-size": 48,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "palm_desert_carbon":
            [
                [
                    {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "font-size": 48,
                        "x": 260,
                        "y": 710,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 48,
                        "x": 1140,
                        "y": 838,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 130,
                        "y": 2584,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 48,
                        "x": 852,
                        "y": 2594,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "perris_carbon":
            [
                [
                    {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "font-size": 48,
                        "x": 325,
                        "y": 917,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 48,
                        "x": 1049,
                        "y": 1029,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 168,
                        "y": 2228,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": today_str,
                        "font-size": 48,
                        "x": 940,
                        "y": 2246,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "redlands_carbon":
            [
                [
                    {
                        "type": "text",
                        "text": today_str,
                        "font-size": 42,
                        "x": 560,
                        "y": 976,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "font-size": 42,
                        "x": 707,
                        "y": 1030,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 42,
                        "x": 707,
                        "y": 1080,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 310,
                        "y": 2677,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": today_str,
                        "font-size": 48,
                        "x": 1640,
                        "y": 2697,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "rialto_carbon":
            [
                [
                     {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "font-size": 48,
                        "x": 468,
                        "y": 1426,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 48,
                        "x": 468,
                        "y": 1590,
                        "rgb": (0, 0, 0)
                    }
                ],
                [
                    {
                        "type": "image",
                        "x": 316,
                        "y": 1233,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": today_str,
                        "font-size": 48,
                        "x": 1710,
                        "y": 1212,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "riverside_carbon":
            [
                [

                ],
                [
                    {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "font-size": 48,
                        "x": 252,
                        "y": 756,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 48,
                        "x": 1482,
                        "y": 768,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 109,
                        "y": 2700,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": today_str,
                        "font-size": 48,
                        "x": 1485,
                        "y": 2702,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "san_bernardino_carbon":
            [
                [
                    {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "font-size": 48,
                        "x": 289,
                        "y": 936,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": formatted_add + " " + formatted_city + ", " + app_entry.customer_state,
                        "font-size": 48,
                        "x": 1526,
                        "y": 931,
                        "rgb": (0, 0, 0)

                    },
                    {
                        "type": "image",
                        "x": 151,
                        "y": 2730,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": today_str,
                        "font-size": 48,
                        "x": 1599,
                        "y": 2724,
                        "rgb": (0, 0, 0)

                    }
                ]
            ],
            "santa_ana_carbon":
            [
                [
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 48,
                        "x": 838,
                        "y": 945,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "font-size": 48,
                        "x": 832,
                        "y": 1133,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 221,
                        "y": 2578,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": today_str,
                        "font-size": 48,
                        "x": 1829,
                        "y": 2571,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "victorville_carbon":
            [
                [
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 48,
                        "x": 640,
                        "y": 2225,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "font-size": 48,
                        "x": 640,
                        "y": 2375,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 90,
                        "y": 2730,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": today_str,
                        "font-size": 48,
                        "x": 1760,
                        "y": 2815,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "wildomar_carbon":
            [
                [
                    {
                        "type": "text",
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "font-size": 48,
                        "x": 606,
                        "y": 1998,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "text": formatted_add,
                        "font-size": 48,
                        "x": 606,
                        "y": 2118,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 114,
                        "y": 2232,
                        "name": "check.jpg"
                    },
                    {
                        "type": "text",
                        "text": today_str,
                        "font-size": 48,
                        "x": 1848,
                        "y": 2238,
                        "rgb": (0, 0, 0)
                    }
                ]
            ],
            "la_county":
            [
                [
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": today_str,
                        "x": 730,
                        "y": 700,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 730,
                        "y": 775,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal,
                        "x": 730,
                        "y": 830,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 340,
                        "y": 1175,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title(),
                        "x": 700,
                        "y": 2240,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_add,
                        "x": 700,
                        "y": 2320,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": formatted_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal,
                        "x": 700,
                        "y": 2395,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "text",
                        "font-size": 48,
                        "text": Helpers.format_phone_number(app_entry.customer_phone),
                        "x": 700,
                        "y": 2575,
                        "rgb": (0, 0, 0)
                    },
                    {
                        "type": "image",
                        "x": 600,
                        "y": 2665,
                        "name": "check.jpg"
                    }
                ],
                [

                ]
            ]
        }

        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        filename = bucket + "/Images/Proposal/Docs/" + doc_name + "/"

        retryParameters = gcs.RetryParams(initial_delay=0.2,
                                               max_delay=5.0,
                                               backoff_factor=2,
                                               max_retry_period=15,
                                               urlfetch_timeout=30)

        page_idx = 0
        page_buffers = []
        img_bytes = []
        usr_img_bytes_dict = {}
        while page_idx < doc_page_count_dict[doc_name]:
            gcs_file = gcs.open(filename + str(page_idx + 1) + ".jpg", 'r', retry_params=retryParameters)

            img_bytes.append(BytesIO(gcs_file.read()))
            gcs_file.close()
            img = Image.open(img_bytes[page_idx])

            for paste_item in paste_data[doc_name][page_idx]:
                if paste_item["type"] == "text":
                    font1 = ImageFont.truetype("Times.ttf", paste_item["font-size"])

                    img2 = Image.new("RGBA", (900,90), (255, 255, 255, 0))
                    draw = ImageDraw.Draw(img2)
                    draw.text((5, 0), paste_item["text"], paste_item["rgb"], font=font1)
                    img.paste(img2, (paste_item["x"], paste_item["y"]), img2)

                elif paste_item["type"] == "image":
                    filename2 = bucket + "/Images/Proposal/Docs/user_images/" + paste_item["name"]
                    gcs_file2 = gcs.open(filename2, 'r', retry_params=retryParameters)

                    img2 = Image.open(BytesIO(gcs_file2.read()))
                    gcs_file2.close()

                    cpy = Image.new("RGBA", img2.size, (255, 255, 255, 0))
                    width = cpy.size[0]
                    height = cpy.size[1]

                    w_cnt = 0
                    while w_cnt < width:
                        h_cnt = 0
                        while h_cnt < height:
                            pixel_data = img2.getpixel((w_cnt, h_cnt))
                            cpy.putpixel((w_cnt, h_cnt), pixel_data)
                            h_cnt += 1

                        w_cnt += 1

                    img.paste(cpy, (paste_item["x"], paste_item["y"]), cpy)





            page_buffers.append(StringIO.StringIO())
            img.save(page_buffers[page_idx], "PDF", resolution=100.0, quality=100.0)
            page_idx += 1

        doc = PdfFileWriter()
        for buff in page_buffers:
            buff.seek(2)
            doc.addPage(PdfFileReader(buff, False).getPage(0))

    if not write_to_gcs:
        return {"doc": doc, "data_to_close": page_buffers + img_bytes + usr_img_bytes_dict.values()}
    else:
        final_buff = StringIO.StringIO()
        doc.write(final_buff)
        bucket_name = os.environ.get('BUCKET_NAME',
                             app_identity.get_default_gcs_bucket_name())

        bucket = '/' + bucket_name
        filename = bucket + '/TempDocs/' + token + "_" + str(doc_idx) + ".pdf"

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file3 = gcs.open(
                        filename,
                        'w',
                        content_type="application/pdf",
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar',
                                 'x-goog-acl': 'public-read'},
                        retry_params=write_retry_params)
        gcs_file3.write(final_buff.getvalue())
        gcs_file3.close()
        final_buff.close()
        for item in page_buffers + img_bytes + usr_img_bytes_dict.values():
            item.close()

