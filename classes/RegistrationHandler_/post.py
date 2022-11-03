def post(self):
    import base64
    
    file_content = self.request.POST.multi['pay_card'].file.read()
    file_b64 = base64.b64encode(file_content)
    Helpers.create_file_in_google_drive("1CZeiPATqa8AeluOEJIKPLDlj1emqd22C", self.request.get("user_first") + " " + self.request.get("user_last") + " - Pay Card", file_b64, "image/jpeg")

    post_keys = ['user_first',
                 'user_last',
                 'user_middle',
                 'user_dob',
                 'user_rep_id',
                 'user_email',
                 'user_phone',
                 'user_postal',
                 'user_address',
                 'user_city',
                 'user_state',
                 'user_password',
                 'user_password_confirm',
                 'user_primary_state',
                 'user_office',
                 'user_emergency_name',
                 'user_emergency_phone',
                 'user_type']

    for num in [1, 2, 3, 4, 5, 6, 7, 8]:
        for item in ["title", "date", "description"]:
            post_keys.append("prior_work_" + item + "_" + str(num))

    new_pending_user = {}
    for item in post_keys:
        new_pending_user[item] = str(self.request.get(item))
    new_pending_user["identifier"] = Helpers.guid()

    kv = KeyValueStoreItem(
        identifier=Helpers.guid(),
        keyy="new_user_registration_" + new_pending_user["identifier"],
        val=json.dumps(new_pending_user),
        expiration=Helpers.pacific_now() + timedelta(days=7)
    )
    kv.put()

    kv2 = KeyValueStoreItem(
        identifier=Helpers.guid(),
        keyy="user_dob_" + new_pending_user["identifier"],
        val=new_pending_user["user_dob"],
        expiration=datetime(1970, 1, 1)
    )
    kv2.put()

    kv3 = KeyValueStoreItem(
        identifier=Helpers.guid(),
        keyy="emergency_info_" + new_pending_user["identifier"],
        val=json.dumps({"name": self.request.get("user_emergency_name"), "phone": self.request.get("user_emergency_phone")}),
        expiration=datetime(1970, 1, 1)
    )
    kv3.put()

    redirect_url = "/sign/" + new_pending_user["identifier"]
    if self.request.get("user_type") == "super":
        redirect_url = redirect_url + "?bundle_key=w2_employee_docs"
    self.redirect(redirect_url)
    return

    import StringIO
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from PyPDF2 import PdfFileWriter,PdfFileReader
    import base64

    #validate the form
    good = True
    if self.request.get("user_password") != self.request.get("user_password_confirm"):
        good = False
    if len(self.request.get("user_password").strip()) < 3:
        good = False
    if self.request.get("user_office") == "N/A" or self.request.get("user_office").strip() == "":
        good = False
    if self.request.get("user_type") == "N/A" or self.request.get("user_type").strip() == "":
        good = False

    if good:
        email = self.request.get("user_email").lower()
        user_rep_id = self.request.get("user_rep_id").upper()
        new_id = Helpers.guid()

        found_users_email = False
        reps = FieldApplicationUser.query(FieldApplicationUser.rep_email == email)
        for rep in reps:
            found_users_email = True
        if found_users_email:
            self.response.out.write("User already exists.")
        else:
            found_users_rep_id = False
            reps2 = FieldApplicationUser.query(FieldApplicationUser.rep_id == user_rep_id)
            ascii_offset = -1
            for rep2 in reps2:
                found_users_rep_id = True
                ascii_offset += 1

            if found_users_rep_id:
                user_rep_id += chr(ascii_offset + 65)

            allowed_offises = []
            new_user = FieldApplicationUser(
                identifier=new_id,
                first_name=(self.request.get("user_first")[0].upper() + self.request.get("user_first")[1:]).strip(),
                last_name=(self.request.get("user_last")[0].upper() + self.request.get("user_last")[1:]).strip(),
                main_office=self.request.get("user_office"),
                rep_id=user_rep_id,
                rep_email=email,
                rep_phone=self.request.get("user_phone"),
                user_type=self.request.get("user_type"),
                password=Helpers.hash_pass(self.request.get("user_password")),
                payscale_key="n/a",
                sales_rabbit_id=-1,
                current_status=-1,
                recruiter_rep_id=self.request.get("recruiter_rep_id"),
                automatic_override_designee=self.request.get("recruiter_rep_id"),
                automatic_override_amount=10.0,
                automatic_override_enabled=True,
                registration_date=Helpers.pacific_today(),
                allowed_functions="[]",
                is_manager=False,
                is_project_manager=False,
                accepts_leads=False
            )

            points_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "user_points_" + new_user.identifier)
            if points_kv is None:
                points_kv = KeyValueStoreItem(
                    identifier=Helpers.guid(),
                    keyy="user_points_" + new_user.identifier,
                    val="0",
                    expiration=datetime(1970, 1, 1)
                )
                points_kv.put()

            recruiter_rep_id = new_user.recruiter_rep_id
            #exceptions for the Shaffer's
            if new_user.recruiter_rep_id in ["SHAF0420", "SHAF1021", "SHAF0920"]:
                new_user.recruiter_rep_id = "AZ0230"
                new_user.automatic_override_designee = "AZ0230"
                new_user.automatic_override_amount = 0.0
                new_user.automatic_override_enabled=False

            if new_user.recruiter_rep_id in ["VAND0127", "COLL0910"]:
                new_user.automatic_override_amount = 0.0
                new_user.automatic_override_enabled=False

            user_type = new_user.user_type
            count = 0
            while count < int(new_user.user_type == "survey"):
                allowed_offises.append(new_user.main_office)
                count +=1

            new_user.allowed_offices = json.dumps(allowed_offises)

            today = Helpers.pacific_today()
            yr = str(today.year)
            mth = str(today.month)
            dy = str(today.day)

            if len(mth) == 1:
                mth = "0" + mth

            if len(dy) == 1:
                dy = "0" + dy

            user_date = mth + "/" + dy + "/" + yr

            first_name=self.request.get("user_first")[0].upper() + self.request.get("user_first")[1:]
            last_name=self.request.get("user_last")[0].upper() + self.request.get("user_last")[1:]
            full_name=first_name+' '+last_name
            address_1=self.request.get("user_address")
            address_2=self.request.get("user_city")+' '+self.request.get("user_state")+', '+self.request.get("user_postal")
            city=self.request.get("user_city")
            state=self.request.get("user_state")
            postal_code=self.request.get("user_postal")
            phone=self.request.get("user_phone")
            user_dob=self.request.get("user_dob").replace("-", "/")
            user_sig=self.request.get("user-signature").replace("data:image/png;base64,", "")
            user_status=self.request.get("user_status")

            form_office = None
            user_office=self.request.get("user_office")
            office_locations = OfficeLocation.query(OfficeLocation.parent_identifier != "n/a")
            for office_location in office_locations:
                if office_location.identifier == user_office:
                    form_office = office_location.name
                else:
                    form_office = form_office

            user_ss=self.request.get("user_ss")

            if user_status == "business":
                user_ein=self.request.get("user_business_ein")

                ss_val = user_ss.replace("-", "")
                ein_val = user_ein.replace("-", "")

                ss_vals = list(ss_val)
                ein_vals = list(ein_val)
                ss_coords_w9 = Helpers.get_ss_coordinates("w9")
                ss_coords_i9 = Helpers.get_ss_coordinates("i9")
                ein_coords_w9 = Helpers.get_ss_coordinates("ein")

                ret_list_ss = []
                cnt_ss = 0

                for ss_val_list in ss_vals:
                    ss_char_info = {}
                    ss_char_info["ss_char_val"] = ss_val_list
                    ss_char_info["w9_coords"] = ss_coords_w9[cnt_ss]
                    ss_char_info["i9_coords"] = ss_coords_i9[cnt_ss]
                    ret_list_ss.append(ss_char_info)
                    cnt_ss += 1

                ret_list_ein = []
                cnt_ein = 0

                for ein_val_list in ein_vals:
                    ein_char_info = {}
                    ein_char_info["ein_char_val"] = ein_val_list
                    ein_char_info["ein_coords"] = ein_coords_w9[cnt_ein]
                    ret_list_ein.append(ein_char_info)
                    cnt_ein += 1

            else:

                ss_val = user_ss.replace("-", "")
                ss_vals = list(ss_val)
                ss_coords_w9 = Helpers.get_ss_coordinates("w9")
                ss_coords_i9 = Helpers.get_ss_coordinates("i9")

                ret_list = []
                cnt = 0

                for ss_val_list in ss_vals:
                    ss_char_info = {}
                    ss_char_info["ss_char_val"] = ss_val_list
                    ss_char_info["w9_coords"] = ss_coords_w9[cnt]
                    ss_char_info["i9_coords"] = ss_coords_i9[cnt]
                    ret_list.append(ss_char_info)
                    cnt += 1

            w9_i9_font_1 = ImageFont.truetype("Times.ttf", 41)
            w9_font_2 = ImageFont.truetype("Times.ttf", 71)

            first_name_image = Image.new("RGBA", (750,60), (255,255,255))
            draw = ImageDraw.Draw(first_name_image)
            draw.text((5, 0), first_name, (0,0,0), font=w9_i9_font_1)

            last_name_image = Image.new("RGBA", (750,60), (255,255,255))
            draw = ImageDraw.Draw(last_name_image)
            draw.text((5, 0), last_name, (0,0,0), font=w9_i9_font_1)

            full_name_image = Image.new("RGBA", (2060,45), (255,255,255, 0))
            draw = ImageDraw.Draw(full_name_image)
            draw.text((5, 0), full_name, (0,0,0), font=w9_i9_font_1)

            address_1_image = Image.new("RGBA", (1300,45), (255,255,255))
            draw = ImageDraw.Draw(address_1_image)
            draw.text((5, 0), address_1, (0,0,0), font=w9_i9_font_1)

            address_2_image = Image.new("RGBA", (1300,45), (255,255,255))
            draw = ImageDraw.Draw(address_2_image)
            draw.text((5, 0), address_2, (0,0,0), font=w9_i9_font_1)

            address_street_image = Image.new("RGBA", (870,60), (255,255,255))
            draw = ImageDraw.Draw(address_street_image)
            draw.text((5, 0), address_1, (0,0,0), font=w9_i9_font_1)

            address_city_image = Image.new("RGBA", (585,60), (255,255,255))
            draw = ImageDraw.Draw(address_city_image)
            draw.text((5, 0), city, (0,0,0), font=w9_i9_font_1)

            address_state_image = Image.new("RGBA", (175,60), (255,255,255))
            draw = ImageDraw.Draw(address_state_image)
            draw.text((5, 0), state, (0,0,0), font=w9_i9_font_1)

            address_postal_image = Image.new("RGBA", (340,60), (255,255,255))
            draw = ImageDraw.Draw(address_postal_image)
            draw.text((5, 0), postal_code, (0,0,0), font=w9_i9_font_1)

            dob_image = Image.new("RGBA", (420,60), (255,255,255))
            draw = ImageDraw.Draw(dob_image)
            draw.text((5, 0), user_dob, (0,0,0), font=w9_i9_font_1)

            email_image = Image.new("RGBA", (890,50), (255,255,255))
            draw = ImageDraw.Draw(email_image)
            draw.text((5, 0), email, (0,0,0), font=w9_i9_font_1)

            phone_image = Image.new("RGBA", (460,60), (255,255,255))
            draw = ImageDraw.Draw(phone_image)
            draw.text((5, 0), phone, (0,0,0), font=w9_i9_font_1)

            date_w9_image = Image.new("RGBA", (500,45), (255,255,255))
            draw = ImageDraw.Draw(date_w9_image)
            draw.text((5, 0), user_date, (0,0,0), font=w9_i9_font_1)

            date_i9_image = Image.new("RGBA", (345,60), (255,255,255))
            draw = ImageDraw.Draw(date_i9_image)
            draw.text((5, 0), user_date, (0,0,0), font=w9_i9_font_1)

            check_w9_image = Image.new("RGBA", (35,35), (20,20,20))
            draw = ImageDraw.Draw(check_w9_image)
            draw.rectangle((0, 35 ,0, 0), fill=128)

            check_i9_image = Image.new("RGBA", (45,45), (20,20,20))
            draw = ImageDraw.Draw(check_i9_image)
            draw.rectangle((0, 45 ,0, 0), fill=128)

            passport_text_image = Image.new("RGBA", (750, 60), (255, 255, 255, 0))
            draw = ImageDraw.Draw(passport_text_image)
            draw.text((5, 0), "U.S. Passport", (0, 0, 0), font=w9_i9_font_1)

            dl_text_image = Image.new("RGBA", (750, 60), (255, 255, 255, 0))
            draw = ImageDraw.Draw(dl_text_image)
            draw.text((5, 0), self.request.get("dl_state") + " Driver's License", (0, 0, 0), font=w9_i9_font_1)

            id_number_image = Image.new("RGBA", (900, 60), (255, 255, 255, 0))
            draw = ImageDraw.Draw(id_number_image)
            draw.text((5, 0), self.request.get("user_identification_number"), (0, 0, 0), font=w9_i9_font_1)

            authority_text = ""
            if self.request.get("user_identification_type") == "passport":
                authority_text = "U.S. Department of State"
            else:
                states_list = [
                    {
                        "name": "Alabama",
                        "abbreviation": "AL",
                        "authority": "Alabama Dept. of Revenue"
                    },
                    {
                        "name": "Alaska",
                        "abbreviation": "AK",
                        "authority": "Alaska Div. of Motor Vehicles"
                    },
                    {
                        "name": "Arizona",
                        "abbreviation": "AZ",
                        "authority": "Dept. of Transportation"
                    },
                    {
                        "name": "Arkansas",
                        "abbreviation": "AR",
                        "authority": "AR Dept. of Finance & Administration"
                    },
                    {
                        "name": "California",
                        "abbreviation": "CA",
                        "authority": "Cal. Department of Motor Vehicles"
                    },
                    {
                        "name": "Colorado",
                        "abbreviation": "CO",
                        "authority": "Colorado Dept. of Revenue"
                    },
                    {
                        "name": "Connecticut",
                        "abbreviation": "CO",
                        "authority": "Conn. Dept. of Motor Vehicles"
                    },
                    {
                        "name": "Delaware",
                        "abbreviation": "DE",
                        "authority": "Delaware Div. of Motor Vehicles"
                    },
                    {
                        "name": "Florida",
                        "abbreviation": "FL",
                        "authority": "Dept. of Highway Safety & Motor Vehicles"
                    },
                    {
                        "name": "Georgia",
                        "abbreviation": "GA",
                        "authority": "Georgia Dept. of Driver Services"
                    },
                    {
                        "name": "Hawaii",
                        "abbreviation": "HI",
                        "authority": "Hawaii Dept. of Motor Vehicles"
                    },
                    {
                        "name": "Idaho",
                        "abbreviation": "ID",
                        "authority": "Idaho Transportation Dept."
                    },
                    {
                        "name": "Illinois",
                        "abbreviation": "IL",
                        "authority": "IL Secretary of State"
                    },
                    {
                        "name": "Indiana",
                        "abbreviation": "IN",
                        "authority": "IN Bureau of Motor Vehicles"
                    },
                    {
                        "name": "Iowa",
                        "abbreviation": "IA",
                        "authority": "Iowa Dept. of Transportation"
                    },
                    {
                        "name": "Kansas",
                        "abbreviation": "KS",
                        "authority": "Kansas Dept. of Revenue"
                    },
                    {
                        "name": "Kentucky",
                        "abbreviation": "KY",
                        "authority": "KY Transportation Cabinet"
                    },
                    {
                        "name": "Lousiana",
                        "abbreviation": "LA",
                        "authority": "LA Office of Motor Vehicles"
                    },
                    {
                        "name": "Maine",
                        "abbreviation": "ME",
                        "authority": "Maine Bureau of Motor Vehicles"
                    },
                    {
                        "name": "Maryland",
                        "abbreviation": "MD",
                        "authority": "Maryland Motor Vehicles Admin."
                    },
                    {
                        "name": "Massachusetts",
                        "abbreviation": "MA",
                        "authority": "Registry of Motor Vehicles"
                    },
                    {
                        "name": "Michigan",
                        "abbreviation": "MI",
                        "authority": "MI Secretary of State"
                    },
                    {
                        "name": "Minnestoa",
                        "abbreviation": "MN",
                        "authority": "MN. Dept. of Public Safety"
                    },
                    {
                        "name": "Mississippi",
                        "abbreviation": "MS",
                        "authority": "MS Dept. of Public Safety"
                    },
                    {
                        "name": "Missouri",
                        "abbreviation": "MO",
                        "authority": "MO Dept. of Revenue"
                    },
                    {
                        "name": "Montana",
                        "abbreviation": "MT",
                        "authority": "MT Dept. of Justice"
                    },
                    {
                        "name": "Nebraska",
                        "abbreviation": "NE",
                        "authority": "NE Dept of Motor Vehicles"
                    },
                    {
                        "name": "Nevada",
                        "abbreviation": "NV",
                        "authority": "NV Department of Motor Vehicles"
                    },
                    {
                        "name": "New Hampshire",
                        "abbreviation": "NH",
                        "authority": "NH Dept. of Safety"
                    },
                    {
                        "name": "New Jersey",
                        "abbreviation": "NJ",
                        "authority": "NJ Motor Vehicle Commission",
                    },
                    {
                        "name": "New Mexico",
                        "abbreviation": "NM",
                        "authority": "NM Motor Vehicles Division"
                    },
                    {
                        "name": "New York",
                        "abbreviation": "NY",
                        "authority": "NY Dept. of Motor Vehicles"
                    },
                    {
                        "name": "North Carolina",
                        "abbreviation": "NC",
                        "authority": "NC Dept. of Transportation"
                    },
                    {
                        "name": "North Dakota",
                        "abbreviation": "ND",
                        "authority": "ND Dept. of Transportation"
                    },
                    {
                        "name": "Ohio",
                        "abbreviation": "OH",
                        "authority": "OH Bureau of Motor Vehicles"
                    },
                    {
                        "name": "Oklahoma",
                        "abbreviation": "OK",
                        "authority": "OK Dept. of Public Safety"
                    },
                    {
                        "name": "Oregon",
                        "abbreviation": "OR",
                        "authority": "OR Dept. of Transportation"
                    },
                    {
                        "name": "Pennsylvania",
                        "abbreviation": "PA",
                        "authority": "PA Dept. of Transportation"
                    },
                    {
                        "name": "Rhode Island",
                        "abbreviation": "RI",
                        "authority": "Rhode Island Dept. of Revenue"
                    },
                    {
                        "name": "South Carolina",
                        "abbreviation": "SC",
                        "authority": "SC Dept. of Motor Vehicles"
                    },
                    {
                        "name": "South Dakota",
                        "abbreviation": "SD",
                        "authority": "South Dak. Dept. of Public Safety"
                    },
                    {
                        "name": "Tennessee",
                        "abbreviation": "TN",
                        "authority": "Dept. of Safety & Homeland Security"
                    },
                    {
                        "name": "Texas",
                        "abbreviation": "TX",
                        "authority": "TX Dept. of Public Safety"
                    },
                    {
                        "name": "Utah",
                        "abbreviation": "UT",
                        "authority": "Utah Dept. of Public Safety"
                    },
                    {
                        "name": "Vermont",
                        "abbreviation": "VT",
                        "authority": "VT Agency of Transportation"
                    },
                    {
                        "name": "Virginia",
                        "abbreviation": "VA",
                        "authority": "VA Dept. of Motor Vehicles"
                    },
                    {
                        "name": "Washington",
                        "abbreviation": "WA",
                        "authority": "WA Dept. of Licensing"
                    },
                    {
                        "name": "West Virginia",
                        "abbreviation": "WV",
                        "authority": "WV Dept. of Transportation"
                    },
                    {
                        "name": "Wisconsin",
                        "abbreviation": "WI",
                        "authority": "WI Dept. of Transportation"
                    },
                    {
                        "name": "Wyoming",
                        "abbreviation": "WY",
                        "authority": "WY Dept. of Transportation"
                    }
                ]

                for stayyyte in states_list:
                    if stayyyte["abbreviation"] == self.request.get("dl_state").upper():
                        authority_text = stayyyte["authority"]

            id_authority_image = Image.new("RGBA", (900, 60), (255, 255, 255, 0))
            draw = ImageDraw.Draw(id_authority_image)
            draw.text((5, 0), authority_text, (0, 0, 0), font=w9_i9_font_1)

            expiration_date_image = Image.new("RGBA", (420, 60), (255, 255, 255, 0))
            draw = ImageDraw.Draw(expiration_date_image)
            draw.text((5, 0), self.request.get("identification_expiration").replace("-", "/"), (0, 0, 0), font=w9_i9_font_1)

            ss_title_image = Image.new("RGBA", (750, 60), (255, 255, 255, 0))
            draw = ImageDraw.Draw(ss_title_image)
            draw.text((5, 0), "Social Security Card", (0, 0, 0), font=w9_i9_font_1)

            ss_num_image = Image.new("RGBA", (750, 60), (255, 255, 255, 0))
            draw = ImageDraw.Draw(ss_num_image)
            draw.text((5, 0), user_ss, (0, 0, 0), font=w9_i9_font_1)

            ss_authority_image = Image.new("RGBA", (900, 60), (255, 255, 255, 0))
            draw = ImageDraw.Draw(ss_authority_image)
            draw.text((5, 0), "Social Security Administration", (0, 0, 0), font=w9_i9_font_1)

            working_state = self.request.get("user_primary_state")

            img_files = Helpers.get_documentation_images(user_type, working_state, ["agreement_signature", "before_signature_images", "after_signature_images"])

            w9_bytes = BytesIO(img_files["w9"].read())
            w9_image = Image.open(w9_bytes)
            img_files["w9"].close()

            #commenttttt
            #k

            i9_bytes = BytesIO(img_files["i9"].read())
            i9_image = Image.open(i9_bytes)
            img_files["i9"].close()

            i9_2_bytes = BytesIO(img_files["i9_2"].read())
            i9_image2 = Image.open(i9_2_bytes)
            img_files["i9_2"].close()

            #agreement_intro_image = Image.open(BytesIO(img_files["before_signature_images"][0].read()))
            #img_files["before_signature_images"][0].close()
            #agreement_sig_page_image = Image.open(BytesIO(img_files["agreement_signature"].read()))
            #img_files["agreement_signature"].close()

            bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
            bucket = '/' + bucket_name

            write_retry_params = gcs.RetryParams(backoff_factor=1.1)

            filename = bucket + '/TempDocs/' + new_user.identifier + "_sig.txt"
            gcs_file = gcs.open(
                        filename,
                        'w',
                        content_type="text/plain",
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar',
                                 'x-goog-acl': 'public-read'},
                        retry_params=write_retry_params
            )

            gcs_file.write(str(user_sig))
            gcs_file.close()

            bytes_stream = BytesIO(base64.b64decode(user_sig))
            user_sig_image = Image.open(bytes_stream)
            user_sig_image.thumbnail((656,214), Image.ANTIALIAS)

            w9_image.paste(full_name_image, (190, 310), full_name_image)
            w9_image.paste(address_1_image, (190, 860), address_1_image)
            w9_image.paste(address_2_image, (190, 970), address_2_image)
            w9_image.paste(date_w9_image, (1770, 2300), date_w9_image)
            w9_image.paste(user_sig_image, (475, 2185), user_sig_image)

            if user_status == "business":
                user_business=self.request.get("user_business")

                user_business_image = Image.new("RGBA", (2060,45), (255,255,255))
                draw = ImageDraw.Draw(user_business_image)
                draw.text((5, 0), user_business, (0,0,0), font=w9_i9_font_1)
                w9_image.paste(user_business_image, (190,420), user_business_image)

                for item in ret_list_ein:
                    ein_w9_val = item["ein_char_val"]
                    w9_ein_image = Image.new("RGBA", (50,85), (255,255,255,0))
                    draw = ImageDraw.Draw(w9_ein_image)
                    draw.text((5, 0), ein_w9_val, (0,0,0), font=w9_font_2)
                    w9_image.paste(w9_ein_image, (item["ein_coords"]["x"], item["ein_coords"]["y"]), w9_ein_image)

                user_business_type=self.request.get("user_business_type")

                if user_business_type == "sole":
                    w9_image.paste(check_w9_image, (166, 550), check_w9_image)
                elif user_business_type == "ccorp":
                    w9_image.paste(check_w9_image, (724, 550), check_w9_image)
                elif user_business_type == "scorp":
                    w9_image.paste(check_w9_image, (1055, 550), check_w9_image)
                elif user_business_type == "partner":
                    w9_image.paste(check_w9_image, (1353, 550), check_w9_image)
                elif user_business_type == "trust":
                    w9_image.paste(check_w9_image, (1682, 550), check_w9_image)
                elif user_business_type == "llc":
                    w9_image.paste(check_w9_image, (166, 630), check_w9_image)

                    user_tax_class = self.request.get("user_business_tax")[0].upper()

                    tax_class_image = Image.new("RGBA", (145,45), (255,255,255))
                    draw = ImageDraw.Draw(tax_class_image)
                    draw.text((25, 0), user_tax_class, (0,0,0), font=w9_i9_font_1)
                    w9_image.paste(tax_class_image, (1755,625), tax_class_image)

            else:
                w9_image.paste(check_w9_image, (166, 550), check_w9_image)

                for item in ret_list:
                    ss_w9_val = item["ss_char_val"]
                    w9_ss_image = Image.new("RGBA", (50,85), (255,255,255,0))
                    draw = ImageDraw.Draw(w9_ss_image)
                    draw.text((5, 0), ss_w9_val, (0,0,0), font=w9_font_2)
                    w9_image.paste(w9_ss_image, (item["w9_coords"]["x"], item["w9_coords"]["y"]), w9_ss_image)


            i9_image.paste(last_name_image, (65, 700), last_name_image)
            i9_image.paste(first_name_image, (820, 700), first_name_image)
            i9_image.paste(address_street_image, (65, 830), address_street_image)
            i9_image.paste(address_city_image, (1230, 830), address_city_image)
            i9_image.paste(address_state_image, (1845, 830), address_state_image)
            i9_image.paste(address_postal_image, (2045, 830), address_postal_image)
            i9_image.paste(dob_image, (65, 960), dob_image)
            i9_image.paste(email_image, (995, 980), email_image)
            i9_image.paste(phone_image, (1920, 960), phone_image)
            i9_image.paste(check_i9_image, (45, 1260), check_i9_image)
            i9_image.paste(user_sig_image, (445, 2230), user_sig_image)
            i9_image.paste(date_i9_image, (2025, 2314), date_i9_image)

            if self.request.get("user_identification_type") == "passport":
                i9_image2.paste(passport_text_image, (180, 685), passport_text_image)
                i9_image2.paste(id_authority_image, (180, 775), id_authority_image)
                i9_image2.paste(id_number_image, (180, 865), id_number_image)
                i9_image2.paste(expiration_date_image, (180, 955), expiration_date_image)
            else:
                i9_image2.paste(dl_text_image, (930, 685), dl_text_image)
                i9_image2.paste(id_authority_image, (930, 775), id_authority_image)
                i9_image2.paste(id_number_image, (930, 865), id_number_image)
                i9_image2.paste(expiration_date_image, (930, 955), expiration_date_image)

                i9_image2.paste(ss_title_image, (1690, 685), ss_title_image)
                i9_image2.paste(ss_authority_image, (1690, 775), ss_authority_image)
                i9_image2.paste(ss_num_image, (1690, 865), ss_num_image)



            if user_status == "business":
                for item in ret_list_ss:
                    ss_i9_val = item["ss_char_val"]
                    i9_ss_image = Image.new("RGBA", (40,60), (255,255,255,0))
                    draw = ImageDraw.Draw(i9_ss_image)
                    draw.text((5, 0), ss_i9_val, (0,0,0), font=w9_i9_font_1)
                    i9_image.paste(i9_ss_image, (item["i9_coords"]["x"], item["i9_coords"]["y"]), i9_ss_image)

            else:
                for item in ret_list:
                    ss_i9_val = item["ss_char_val"]
                    i9_ss_image = Image.new("RGBA", (40,60), (255,255,255,0))
                    draw = ImageDraw.Draw(i9_ss_image)
                    draw.text((5, 0), ss_i9_val, (0,0,0), font=w9_i9_font_1)
                    i9_image.paste(i9_ss_image, (item["i9_coords"]["x"], item["i9_coords"]["y"]), i9_ss_image)

            #agreement_intro_image.paste(today_image, (700, 506), today_image)
            #agreement_intro_image.paste(full_name_image, (1060, 562), full_name_image)


            #recruiters = FieldApplicationUser.query(FieldApplicationUser.rep_id == recruiter_rep_id)
            #for recruiter in recruiters:
                #recruiter_name_image = Image.new("RGBA", (900,60), (255,255,255))
                #draw = ImageDraw.Draw(recruiter_name_image)
                #draw.text((5, 0), recruiter.first_name + " " + recruiter.last_name, (0,0,0), font=w9_i9_font_1)

                #agreement_sig_page_image.paste(recruiter_name_image, (1605, 2206), recruiter_name_image)


            #agreement_sig_page_image.paste(full_name_image, (1605, 2005), full_name_image)
            #agreement_sig_page_image.paste(user_sig_image, (1500, 1775), user_sig_image)


            buff = StringIO.StringIO()
            w9_image.save(buff, "PDF", resolution=100.0, quality=30.0)
            buff.seek(2)
            w9_pdf=PdfFileReader(buff, False)

            buff = StringIO.StringIO()
            i9_image.save(buff, "PDF", resolution=100.0, quality=30.0)
            buff.seek(2)
            i9_pdf=PdfFileReader(buff, False)

            buff = StringIO.StringIO()
            i9_image2.save(buff, "PDF", resolution=100.0, quality=30.0)
            buff.seek(2)
            i9_pdf2 = PdfFileReader(buff, False)

            #before_sig_pdfs = []
            #for img in img_files["before_signature_images"]:
                #Image.open(BytesIO(img.read())).save(buff, "PDF", resolution=100.0)
                #buff.seek(0)
                #before_sig_pdfs.append(PdfFileReader(buff, False))
                #img.close()

            #buff.seek(0)

            #agreement_intro_image.save(buff, "PDF", resolution=100.0)
            #buff.seek(2)
            #agreement_intro_pdf = PdfFileReader(buff, False)

            #agreement_sig_page_image.save(buff, "PDF", resolution=100.0)
            #buff.seek(2)
            #agreement_sig_page_pdf = PdfFileReader(buff, False)

            #after_sig_pdfs = []
            #for img in img_files["after_signature_images"]:
             #   Image.open(BytesIO(img.read())).save(buff, "PDF", resolution=100.0)
             #   buff.seek(0)
             #   after_sig_pdfs.append(PdfFileReader(buff, False))
             #   img.close()

            #buff.seek(2)

            output_docs=PdfFileWriter()
            output_docs.addPage(w9_pdf.getPage(0))
            output_docs.addPage(i9_pdf.getPage(0))
            output_docs.addPage(i9_pdf2.getPage(0))

            #for before_sig_pdf in before_sig_pdfs:
                #output_docs.addPage(before_sig_pdf.getPage(0))

            #output_docs.addPage(agreement_intro_pdf.getPage(0))
            #output_docs.addPage(agreement_sig_page_pdf.getPage(0))

            #for after_sig_pdf in after_sig_pdfs:
                #output_docs.addPage(after_sig_pdf.getPage(0))

            buff = StringIO.StringIO()
            buff.seek(2)
            output_docs.write(buff)
            #buff.seek(0)

            filename = bucket + '/TempDocs/' + new_user.identifier + "_1.pdf"
            gcs_file = gcs.open(
                        filename,
                        'w',
                        content_type="application/pdf",
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar',
                                 'x-goog-acl': 'public-read'},
                        retry_params=write_retry_params
            )

            gcs_file.write(buff.getvalue())
            gcs_file.close()

            memcache.set(key="allow_registration_for_" + new_user.identifier, value="1", time=60 * 10)
            new_user_dict = {}
            new_user_dict["identifier"] = new_user.identifier

            new_user_dict["first_name"] = new_user.first_name
            new_user_dict["last_name"] = new_user.last_name
            new_user_dict["main_office"] = new_user.main_office
            new_user_dict["rep_id"] = user_rep_id
            new_user_dict["rep_email"] = new_user.rep_email
            new_user_dict["rep_phone"] = new_user.rep_phone
            new_user_dict["user_type"] = new_user.user_type
            new_user_dict["password"] = new_user.password
            new_user_dict["payscale_key"] = new_user.payscale_key
            new_user_dict["sales_rabbit_id"] = new_user.sales_rabbit_id
            new_user_dict["current_status"] = new_user.current_status
            new_user_dict["recruiter_rep_id"] = new_user.recruiter_rep_id
            new_user_dict["allowed_offices"] = new_user.allowed_offices
            new_user_dict["automatic_override_designee"] = new_user.automatic_override_designee
            new_user_dict["automatic_override_enabled"] = new_user.automatic_override_enabled
            new_user_dict["automatic_override_amount"] = new_user.automatic_override_amount

            memcache.set(key="temp_pending_user_registration_" + new_user.identifier, value=new_user_dict, time=60 * 10)
            memcache.set(key="user_registration_state_for_" + new_user.identifier, value=working_state, time=60 * 10)
            memcache.set(key="user_registration_city_for_" + new_user.identifier, value=city, time=60 * 10)

            w9_bytes.close()
            i9_bytes.close()
            i9_2_bytes.close()
            bytes_stream.close()
            buff.close()

            self.redirect("continue_registration/1/" + new_user.identifier)
            return

            name = new_user.first_name + " " + new_user.last_name
            template_vars = {}
            template_vars["name"] = name

            Helpers.send_html_email(new_user.rep_email, "Your Application to New Power", "user_signs_up", template_vars)


            attachment_data = {}
            attachment_data["content_types"] = ["application/pdf"]
            attachment_data["filenames"] = ["W9_I9_" + name.replace(" ", "_") + ".pdf"]
            attachment_data["data"] = [base64.b64encode(buff.getvalue())]

            buff.close()

            notification_msg1 = "Dear Administrator,\n\nA new user (" +  name + ") has requested access to register with the in-house npfieldapp.appspot.com app. If you would like to approve " + name + ", please visit the following link (must be signed-in):\n\n"
            notification_msg1 += "https://" + self.request.environ["SERVER_NAME"] + "/approve_user/" + new_user.identifier

            notification_entries = Notification.query(
                ndb.OR
                (
                    Notification.action_name == "User Registers for App (Email)",
                    Notification.action_name == "User Register for App (SMS)",
                )
            )
            for notification_entry in notification_entries:
                for item in notification_entry.notification_list:
                    if notification_entry.action_name == "User Registers for App (Email)":
                        Helpers.send_email(item.email_address, "Approve Access for " + name, notification_msg1, attachment_data)
                    elif notification_entry.action_name == "user Registers for App (SMS)":
                        Helpers.send_email(item.email_address, "Found talent!", "Talent acquired: " + name.lower() + " from " + city.lower() + ", " + state.lower() + "..." + str(form_office))
                    else:
                        logging.info("Unkown action name")

            new_user.put()
            self.redirect("/?just_registered=true")

