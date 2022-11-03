def accepts_leads_assignment(self):
    user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not user is None:
        user.accepts_leads = (self.request.get("accepts_leads") == "1")
        user.put()
