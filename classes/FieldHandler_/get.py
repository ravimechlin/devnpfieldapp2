def get(self):
    if "field" in self.request.environ["PATH_INFO"]:
        self.redirect("/sales")
    else:
        try:
            self.session = get_current_session()
            template_values = {}
            template_values["user_name"] = str(self.session["user_name"])
            template_values["rep_phone"] = Helpers.format_phone_number(str(self.session["user_phone"]))
            template_values["rep_email"] = str(self.session["user_email"])
            template_values["rep_id"] = str(self.session["user_rep_id"]).upper()
            template_values["rep_office"] = self.session["user_rep_office"]
            template_values["utility_providers"] = json.dumps(Helpers.read_setting("utility_providers"))

            offices = []
            office_locations = OfficeLocation.query(OfficeLocation.parent_identifier != "n/a")
            for office_location in office_locations:
                office = {}
                office["identifier"] = office_location.identifier
                office["name"] = office_location.name
                offices.append(office)

            template_values["offices"] = json.dumps(offices)

            if str(self.session["user_name"]) == "":
                self.session.non_existent_method("foo", "bar")

            path = Helpers.get_html_path("field_form_v2.html")

            self.response.out.write(template.render(path, template_values))
        except:
            self.response.out.write(".")

