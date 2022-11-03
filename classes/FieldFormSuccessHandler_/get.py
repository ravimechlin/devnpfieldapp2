def get(self):
    self.session = get_current_session()
    keyy = "allow_CPF_work_for_" + self.request.get("e_identifier")
    val = memcache.get(keyy)
    if val == "true":
        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier == self.request.get("e_identifier"))
        for app_entry in app_entries:
            bookings = SurveyBooking.query(SurveyBooking.identifier == self.request.get("b_identifier"))
            for booking in bookings:
                try:
                    template_values = {}
                    template_values["user_name"] = str(self.session["user_name"])
                    template_values["slot"] = "Slot #" + str(booking.slot_number)
                    template_values["date"] = str(booking.booking_month) + "/" + str(booking.booking_day) + "/" + str(booking.booking_year)
                    template_values["cust_name"] = app_entry.customer_first_name + " " + app_entry.customer_last_name
                    template_values["app_entry_identifier"] = app_entry.identifier
                    template_values["booking_identifier"] = booking.identifier

                    path = Helpers.get_html_path('confirmation.html')
                    self.response.out.write(template.render(path, template_values))

                except:
                    self.redirect("/?session_lost=true")

