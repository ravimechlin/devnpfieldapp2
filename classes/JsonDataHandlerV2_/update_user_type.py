def update_user_type(self):
    user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not user is None:
        user.user_type = self.request.get("type")
        user.put()
