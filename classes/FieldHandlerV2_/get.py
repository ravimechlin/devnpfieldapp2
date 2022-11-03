def get(self):
    prepop_info = {}
    import json
    source = "manual"
    if "field" in self.request.environ["PATH_INFO"]:
        self.redirect("/sales")
    else:
        if 5 == 5:
            self.session = get_current_session()
            
            if len(str(self.request.get("token"))) >= 128:
                user_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pass_off_login_" + self.request.get("token"))
                if not user_kv is None:
                    u = FieldApplicationUser.first(
                        ndb.AND(
                            FieldApplicationUser.current_status == 0,
                            FieldApplicationUser.identifier == user_kv.val
                        )
                    )
                    if not u is None:
                        self.session.terminate()
                        self.session["user_identifier"] = u.identifier
                        self.session["user_type"] = u.user_type
                        self.session["user_name"] = u.first_name.strip().title() + " " + u.last_name.strip().title()
                        self.session["user_phone"] = u.rep_phone
                        self.session["user_email"] = u.rep_email
                        self.session["user_rep_id"] = u.rep_id
                        self.session["user_rep_office"] = u.main_office
                        user_kv.key.delete()

                        info_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pass_off_info_" + self.request.get("token"))
                        if not info_kv is None:
                            prepop_info = info_kv.val
                            source = "app"

            template_values = {}
            template_values["user_type"] = str(self.session["user_type"])
            template_values["pre_populated_info"] = prepop_info
            template_values["user_name"] = str(self.session["user_name"])
            template_values["rep_phone"] = Helpers.format_phone_number(str(self.session["user_phone"]))
            template_values["rep_email"] = str(self.session["user_email"])
            template_values["rep_id"] = str(self.session["user_rep_id"]).upper()
            template_values["rep_office"] = self.session["user_rep_office"]
            template_values["user_identifier"] = self.session["user_identifier"]

            closers = FieldApplicationUser.query(
                ndb.AND(
                    FieldApplicationUser.current_status == 0,
                    FieldApplicationUser.user_type.IN(["energy_expert", "sales_manager"])
                )
            )

            closers_list = {}
            for closer in closers:
                closers_list[closer.identifier] = closer.first_name.strip().title() + " " + closer.last_name.strip().title()

            template_values["closers_dict"] = json.dumps(closers_list)

            reader_data = []
            readers = SolarReader.query(SolarReader.rep_ownership == self.session["user_identifier"])
            for reader in readers:
                reader_data.append(reader.hash.upper())

            template_values["reader_data"] = json.dumps(reader_data)
            
            user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.session["user_identifier"])
            if not user is None:
                eight_days_ago = Helpers.pacific_now() + timedelta(days=-8)
                template_values["newbie"] = str(int(user.registration_date >= eight_days_ago.date()))
            
            template_values["utility_providers"] = json.dumps(Helpers.read_setting("utility_providers"))
            template_values["source"] = source

            offices = []
            office_locations = OfficeLocation.query(
                ndb.AND
                (
                    OfficeLocation.active == True,
                    OfficeLocation.is_parent == False
                )
            )
            for office_location in office_locations:
                office = {}
                office["identifier"] = office_location.identifier
                office["name"] = office_location.name
                offices.append(office)

            template_values["offices"] = json.dumps(offices)

            if str(self.session["user_name"]) == "":
                self.session.non_existent_method("foo", "bar")

            path = Helpers.get_html_path("field_form_v2.html")
            
            h_p_t = Helpers.pacific_today()
            if h_p_t.isoweekday() == 6:
                h_p_n = Helpers.pacific_now()
                if h_p_n.hour >= 18:
                    h_p_n = h_p_n + timedelta(days=1)
                    h_p_t = h_p_n.date()
                    
            start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
            while not start_dt.isoweekday() == 7:
                start_dt = start_dt + timedelta(days=-1)

            start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
            end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
            end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

            start_dt = start_dt + timedelta(days=-7)
            end_dt = end_dt + timedelta(days=-7)

            #goal = RepGoal.first(
            #    ndb.AND(
            #        RepGoal.start_date >= start_dt.date(),
            #        RepGoal.rep_identifier == template_values["user_identifier"]
            #    )
            #)
            goal = "Not None"
            if goal is None:
                path = Helpers.get_html_path('goals.html')
                template_values["last_week_start"] = str(start_dt.date())
                template_values["last_week_end"] = str(end_dt.date())

            passwords = Helpers.read_setting("passwords")
            for password in passwords:
                if password["name"] == "Data Logger Required Override Code":
                    template_values["dl_override_code"] = password["password"]

            reps = FieldApplicationUser.query(
                ndb.AND(
                    FieldApplicationUser.accepts_leads == True,
                    FieldApplicationUser.current_status == 0,
                    FieldApplicationUser.main_office == self.session["user_rep_office"]
                )
            )
            closer_data = []
            for rep in reps:
                obj = {"identifier": rep.identifier}
                obj["name"] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
                closer_data.append(obj)
            template_values["closers"] = json.dumps(closer_data)

            cutoff_date = Helpers.pacific_now()
            holidays = []
            holidays_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "company_holidays")
            if not holidays_kv is None:
                holidays = json.loads(holidays_kv.val)

            business_day_ceiling = 4

            #riverside only
            if self.session["user_rep_office"] == "b9878e9d5d74dbaceb7b7d9c1be74fa5ccd87d6100cad5496d2306366bbcfadafca3d2ae5dcfc3a82c2525650a88e4332cfc11183f8a0fd39071f13614e5806f":
                #business_day_ceiling = 4
                business_day_ceiling = 4

            now_for_holidays = Helpers.pacific_now()
            done = False
            business_day_tally = 0
            while not done:
                current_date = now_for_holidays.date()
                is_weekend = current_date.isoweekday() == 6 or current_date.isoweekday() == 7
                is_holiday = str(current_date) in holidays

                business_day_tally += int((not is_weekend) and (not is_holiday))

                done = (business_day_tally == business_day_ceiling)
                now_for_holidays = now_for_holidays + timedelta(days=1)

            #now_for_holidays = now_for_holidays + timedelta(days=-1)
            template_values["cutoff_date"] = str(now_for_holidays.date())

            self.response.out.write(template.render(path, template_values))
        else:
            self.response.out.write(".")

