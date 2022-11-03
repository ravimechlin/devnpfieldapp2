def update_customer_details_from_leads_tab(self):
    payload = json.loads(self.request.get("payload"))
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("identifier"))
    if not app_entry is None:
        app_entry.customer_first_name = payload["first_name"].strip().title()
        app_entry.customer_last_name = payload["last_name"].strip().title()
        app_entry.customer_address = payload["address"].strip()
        app_entry.customer_city = payload["city"].strip().title()
        app_entry.customer_state = payload["state"].upper().strip()
        app_entry.customer_postal = payload["postal"].strip()
        app_entry.customer_phone = payload["phone"]
        app_entry.customer_email = payload["email"]

        app_entry.put()

        booking = SurveyBooking.first(SurveyBooking.field_app_identifier == self.request.get("identifier"))
        if not booking is None:
            booking.name = app_entry.customer_first_name + " " + app_entry.customer_last_name
            booking.address = app_entry.customer_address
            booking.city = app_entry.customer_city
            booking.state = app_entry.customer_state
            booking.postal = app_entry.customer_postal
            booking.phone_number = app_entry.customer_phone
            booking.email = app_entry.customer_email

            booking.put()
