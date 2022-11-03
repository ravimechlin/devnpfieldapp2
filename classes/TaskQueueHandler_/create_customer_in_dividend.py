def create_customer_in_dividend(self):
    from google.appengine.api import app_identity

    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("identifier"))
    if not app_entry is None:
        if str(self.request.get("second_homeowner")) == "1":
            info = json.loads(self.request.get("second_homeowner_dict"))
            app_entry.customer_first_name = info["first_name"]
            app_entry.customer_last_name = info["last_name"]
            app_entry.customer_email = info["email"]
            Helpers.create_customer_in_dividend(app_entry, self.request.get("annual_income"), self.request.get("monthly_mortgage"), info["last_four"])
        else:
            Helpers.create_customer_in_dividend(app_entry, self.request.get("annual_income"), self.request.get("monthly_mortgage"), self.request.get("last_four"))
