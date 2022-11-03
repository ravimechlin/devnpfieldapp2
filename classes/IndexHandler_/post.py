def post(self):
    self.session = get_current_session()
    email_or_id = self.request.get("rep_email_id")
    if "@" in email_or_id:
        email_or_id = email_or_id.lower()
    else:
        email_or_id = email_or_id.upper()
    hashed_pass = Helpers.hash_pass(self.request.get("rep_pass"))
    user_id = ""
    user_type = ""
    user_name = ""
    user_email = ""
    user_phone = ""
    user_rep_id = ""
    user_office = 1
    user_manager = False
    found = False

    users1 = FieldApplicationUser.query(
        ndb.AND
        (
            FieldApplicationUser.rep_email == email_or_id,
            FieldApplicationUser.password == hashed_pass,
            FieldApplicationUser.current_status == 0
        )
    )
    for user in users1:
        found = True
        user_id = user.identifier
        user_type = user.user_type
        user_name = user.first_name + " " + user.last_name
        user_phone = user.rep_phone
        user_email = user.rep_email
        user_rep_id = user.rep_id
        user_office = user.main_office
        user_manager = user.is_manager

    users2 = FieldApplicationUser.query(
        ndb.AND
        (
            FieldApplicationUser.rep_id == email_or_id,
            FieldApplicationUser.password == hashed_pass,
            FieldApplicationUser.current_status == 0
        )
    )
    for user in users2:
        found = True
        user_id = user.identifier
        user_type = user.user_type
        user_name = user.first_name + " " + user.last_name
        user_phone = user.rep_phone
        user_email = user.rep_email
        user_rep_id = user.rep_id
        user_office = user.main_office
        user_manager = user.is_manager

    if found:
        self.session.terminate()
        self.session["user_identifier"] = user_id
        self.session["user_type"] = user_type
        self.session["user_name"] = user_name
        self.session["user_phone"] = user_phone
        self.session["user_email"] = user_email
        self.session["user_rep_id"] = user_rep_id
        self.session["user_rep_office"] = str(user_office)
        self.session["manager"] = str(int(user_manager))
        redirect_url = "/"
        if not str(self.request.get("next_url")) == "":
            redirect_url = base64.b64decode(self.request.get("next_url"))

        #ray and partners
        #if not self.session["user_email"] in ["rnirnber@gmail.com", "thomas@newpower.net", "reimer@newpower.net", "mcollins@newpower.net", "vjones@newpower.net", "ahoman@newpower.net", "ericm@newpower.net", "mschauers@newpower.net", "dallin@newpower.net", "armstrong_tay@hotmail.com", "ahill@newpower.net", "roliver@newpower.net", "dodell@newpower.net", "dlaws@newpower.net"]:
        #    self.session.terminate()
        #    self.response.content_type = "text/plain"
        #    self.response.out.write("Stay strong, stay safe, see ya soon!")
        #    return

        self.redirect(redirect_url)

    else:
        self.session["login_error"] = "true"
        url = "/?error=true"
        if not str(self.request.get("next_url")) == "":
            url += "&next_url=" + self.request.get("next_url")
        self.redirect(url)
