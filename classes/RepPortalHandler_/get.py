def get(self):
    try:
        self.session = get_current_session()

        template_values = {}
        template_values["user_name"] = str(self.session["user_name"])
        template_values["show_lurker_message"] = str(int(Helpers.images_equal("/Images/ProfilePictures/Full/" + self.session["user_identifier"] + ".jpg", "/Images/default.jpg")))
        template_values["user_identifier"] = self.session["user_identifier"]
        template_values["rep_phone"] = Helpers.format_phone_number(str(self.session["user_phone"]))
        template_values["rep_email"] = str(self.session["user_email"])
        template_values["rep_id"] = str(self.session["user_rep_id"]).upper()
        template_values["rep_office"] = self.session["user_rep_office"]
        template_values["user_type"] = str(self.session["user_type"])
        template_values["deal_closing_checklists"] = json.dumps(Helpers.read_setting("deal_closing_checklists"))
        template_values["points_banked"] = "0"
        template_values["tax_brackets_json"] = json.dumps(Helpers.read_setting("tax_brackets"))
        template_values["is_manager"] = "0"
        template_values["manager"] = self.session["manager"]
        template_values["carve_out"] = "0"

        carve_out = Helpers.read_setting("carve_out")
        for c in carve_out:
            if c["identifier"] == template_values["user_identifier"]:
                template_values["carve_out"] = "1"
                template_values["carve_out_number"] = str(c["amount"])

        try:
            template_values["assumed"] = str(self.session["assumed"])
        except:
            template_values["assumed"] = "0"

        if not template_values["assumed"] == "0":
            template_values["carve_out"] = "0"

        usr = FieldApplicationUser.first(FieldApplicationUser.identifier == self.session["user_identifier"])
        if not usr is None:
            template_values["is_manager"] = str(int(usr.is_manager))
        points_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "user_points_" + self.session["user_identifier"])
        if not points_kv is None:
            template_values["points_banked"] = points_kv.val
        
        if str(self.session["user_name"]) == "":
            self.session.non_existent_method("foo", "bar")

        field_app_ids_to_query = ["-1"]
        index = search.Index(name="cust_names")

        results = index.search(self.session["user_rep_id"])
        for result in results:
            for field in result.fields:
                if field.name == "cust_identifier":
                    field_app_ids_to_query.append(field.value)

        template_values["unread_note_count"] = CustomerNote.query(
            ndb.AND
            (
                CustomerNote.field_app_identifier.IN(field_app_ids_to_query),
                CustomerNote.read == False
            )
        ).count()

        template_values["accepts_leads"] = "0"
        template_values["accepts_leads_css"] = "none"
        user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.session["user_identifier"])
        if not user is None:
            template_values["accepts_leads"] = str(int(user.accepts_leads))
            if user.accepts_leads:
                template_values["accepts_leads_css"] = "inline"

        template_values["accepts_leads_text"] = "Not accepting same-days"
        template_values["accepts_leads_css_class"] = "not_accepting"

        today = Helpers.pacific_today()
        accepts_leads_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "accepts_leads_" + str(today) + "_" + self.session["user_identifier"])
        if not accepts_leads_kv is None:
            hours = int(accepts_leads_kv.val.split(":")[0])
            minutes = int(accepts_leads_kv.val.split(":")[1])

            am_pm = "AM"
            if hours >= 12:
                am_pm = "PM"
            if hours > 12:
                hours -= 12

            hours_str = str(hours)
            if len(hours_str) == 1:
                hours_str = "0" + hours_str
            min_str = str(minutes)
            if len(min_str) == 1:
                min_str = "0" + min_str

            template_values["accepts_leads_text"] = "Accepting same-days until " + hours_str + ":" + min_str + " " + am_pm
            template_values["accepts_leads_css_class"] = "accepting"

        template_values["required_actions_count"] = RepRequiredAction.query(
            ndb.AND
            (
                RepRequiredAction.rep_identifier == self.session["user_identifier"],
                RepRequiredAction.completed == datetime(1970, 1, 1)
            )
        ).count()

        field_app_ids_to_query = ["-1"]
        index = search.Index(name="cust_names")

        results = index.search(self.session["user_rep_id"])
        for result in results:
            for field in result.fields:
                if field.name == "cust_identifier":
                    field_app_ids_to_query.append(field.value)

        template_values["save_me_count"] = FieldApplicationEntry.query(
            ndb.AND
            (
                FieldApplicationEntry.identifier.IN(field_app_ids_to_query),
                FieldApplicationEntry.save_me == True
            )
        ).count()

        is_sunday = True
        path = Helpers.get_html_path('rep_portal.html')
        h_p_t = Helpers.pacific_today()
        if h_p_t.isoweekday() == 6:
            h_p_n = Helpers.pacific_now()
            if h_p_n.hour >= 18:
                h_p_n = h_p_n + timedelta(days=1)
                h_p_t = h_p_n.date()
        start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
        while not start_dt.isoweekday() == 7:
            is_sunday = False
            start_dt = start_dt + timedelta(days=1)

        start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

        start_dt = start_dt + timedelta(days=-14)
        if is_sunday:
            start_dt = start_dt + timedelta(days=7)
        end_dt = end_dt + timedelta(days=-7)

        #goal = RepGoal.first(
        #    ndb.AND(
        #        RepGoal.start_date >= start_dt.date(),
        #        RepGoal.rep_identifier == template_values["user_identifier"]
        #    )
        #)
        goal = "Not None"
        if (goal is None) and (not str(self.session["user_name"]) == "solar_pro"):
            path = Helpers.get_html_path('goals.html')
            template_values["last_week_start"] = str(start_dt.date())
            template_values["last_week_end"] = str(end_dt.date())

        template_values["n00b"] = 0
        user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.session["user_identifier"])
        if not user is None:
            if (user.registration_date >= (Helpers.pacific_now() + timedelta(days=-7 * 6)).date()) and user.registration_date >= date(2019, 4, 17):
                template_values["n00b"] = 1

        self.response.out.write(template.render(path, template_values))
    except:
        self.response.out.write(".")

