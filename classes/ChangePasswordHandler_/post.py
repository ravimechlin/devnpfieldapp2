def post(self):
    token = self.request.get("token")
    identifier = self.request.get("identifier")
    key = "reset_token_for_" + identifier
    val = memcache.get(key)

    if not val is None:
        if val == token:
            password = self.request.get("pass")
            hashed_pass = Helpers.hash_pass(password)

            users = FieldApplicationUser.query(FieldApplicationUser.identifier == identifier)
            for user in users:
                user.password = hashed_pass
                user.put()

    self.redirect("/")

