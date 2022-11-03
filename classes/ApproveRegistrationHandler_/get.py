def get(self, user_identifier):
    import base64
    self.session = get_current_session()
    logged_in = True
    try:
        if str(self.session["user_name"]) == "" or str(self.session["user_type"]) != "super":
            self.session.non_existent_method("foo", "bar")
    except:
        logged_in = False

    if logged_in:
        template_values = {}
        template_values["user_name"] = str(self.session["user_name"])
        template_values["app_bucket"] = app_identity.get_default_gcs_bucket_name()
        path = Helpers.get_html_path('approve_user.html')

        users = FieldApplicationUser.query(FieldApplicationUser.identifier == user_identifier)
        for user in users:
            template_values["register_user_identifier"] = user.identifier
            template_values["register_user_name"] = user.first_name + " " + user.last_name
            template_values["register_user_type"] = user.user_type
            template_values["register_user_phone"] = user.rep_phone
            template_values["register_user_email"] = user.rep_email
            template_values["register_main_office"] = user.main_office
            template_values["register_current_status"] = user.current_status

        self.response.out.write(template.render(path, template_values))

    else:
        self.redirect("/?next_url=" + base64.b64encode(self.request.url))

