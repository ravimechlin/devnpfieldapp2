def get(self):
    self.session = get_current_session()
    user_id = ""
    user_type = ""
    logged_in = True
    login_error = False

    try:
        user_id = self.session["user_identifier"]

        if user_id == "9ab5392114c0b530dfe224fafa1d820993f530539f794a95888dbb6a4b2893891453242ea94bf99e87477b87b7eeb35605921a8aacda91aa82bed6dd006adf3c":
            self.session["user_type"] = "field"

        user_type = self.session["user_type"]
    except:
        logged_in = False
        try:
            if "login_error" in self.session.keys():
                if self.session["login_error"] == "true":
                    login_error = True
        except:
            login_error = False
    if not logged_in:
        template_values = {}
        template_values["login_error"] = str(int(login_error))
        path = Helpers.get_html_path('login.html')
        self.response.out.write(template.render(path, template_values))
    else:
        self.session["login_error"] = "false"
        if user_type in ["field", "asst_mgr", "co_mgr", "sales_dist_mgr", "rg_mgr", "solar_pro", "solar_pro_manager", "energy_expert", "sales_manager"]:
            self.redirect("/rep")
        elif user_type == "survey":
            self.redirect("/surveyor")
        elif user_type == "super":
            self.redirect("/super")
        else:
            self.response.out.write("..")

