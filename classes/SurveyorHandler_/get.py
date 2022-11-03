def get(self):
    self.session = get_current_session()

    try:

        if str(self.session["user_name"]) == "" or str(self.session["user_type"]) != "super":
            if str(self.session["user_type"]) != "survey":
                self.session.non_existent_method("foo", "bar")

        fund_sources = Helpers.list_funds()
        tweeked_fund_sources = {}
        for fund_source in fund_sources:
            tweeked_fund_sources[str(fund_source["value"])] = str(fund_source["value_friendly"])

        logging.info(tweeked_fund_sources)
        template_values = {}
        template_values["fund_sources_json"] = json.dumps(tweeked_fund_sources)
        template_values["user_name"] = str(self.session["user_name"])
        template_values["survey_identifier"] = Helpers.get_surveyor_checklist_identifier()
        template_values["o_id"] = self.session["user_rep_office"]

        offices = []
        admin_allowed_offices = []
        office_locations = OfficeLocation.query(OfficeLocation.parent_identifier != "n/a")
        for office_location in office_locations:
            office = {}
            office["identifier"] = office_location.identifier
            office["name"] = office_location.name
            offices.append(office)
            admin_allowed_offices.append(office_location.identifier)

        template_values["offices"] = json.dumps(offices)
        template_values["allowed_offices"] = "[]"
        users = FieldApplicationUser.query(FieldApplicationUser.identifier == str(self.session["user_identifier"]))
        for user in users:
            template_values["allowed_offices"] = user.allowed_offices

        if str(self.session["user_type"]) == "super":
            template_values["allowed_offices"] = json.dumps(admin_allowed_offices)


        path = Helpers.get_html_path('survey.html')
        self.response.out.write(template.render(path, template_values))

    except:
        self.response.out.write("**")

