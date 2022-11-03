def post(self, action=""):
    if action == "new":
        user = FieldApplicationUser.first(
            ndb.AND
            (
                FieldApplicationUser.rep_email == self.request.get("email"),
                FieldApplicationUser.password == Helpers.hash_pass(self.request.get("password")),
                FieldApplicationUser.current_status == 0
            )
        )
        if not user is None:
            hash = Helpers.hash_pass(user.password + "_" + user.identifier)
            auth = AuthKey(
                identifier=Helpers.guid(),
                user_identifier=user.identifier,
                token=hash
            )
            existing_auth = AuthKey.first(
                ndb.AND
                (
                    AuthKey.user_identifier == user.identifier,
                    AuthKey.token == hash
                )
            )
            if existing_auth is None:
                auth.put()

            self.response.out.write(auth.token)
        else:
            self.response.set_status(401)

    elif action == "acquire_session":
        self.session = get_current_session()
        token = self.request.get("token")
        auth_key = AuthKey.first(AuthKey.token == token)
        if not auth_key is None:
            user = FieldApplicationUser.first(FieldApplicationUser.identifier == auth_key.user_identifier)
            if not user is None:
                hash = Helpers.hash_pass(user.password + "_" + user.identifier)
                if hash == token and user.current_status == 0:
                    self.session["user_identifier"] = user.identifier
                    self.session["user_type"] = user.user_type
                    self.session["user_name"] = user.first_name + " " + user.last_name
                    self.session["user_phone"] = user.rep_phone
                    self.session["user_email"] = user.rep_email
                    self.session["user_rep_id"] = user.rep_id
                    self.session["user_rep_office"] = str(user.main_office)

                    self.response.out.write("acquired")
                    return

        self.response.set_status(401)

