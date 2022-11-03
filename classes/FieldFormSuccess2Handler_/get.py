def get(self):
    keyy = "allow_CPF_work_for_" + self.request.get("e_identifier")
    val = memcache.get(keyy)

    if val == "true":
        memcache.delete(keyy)

    template_values = {}
    template_values["message"] = ""
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("e_identifier"))
    booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
    cc = CreditCheck.first(CreditCheck.field_app_identifier == app_entry.identifier)
    if (not cc is None) and (not app_entry is None) and (not booking is None):
        if cc.score > -1:
            if not booking.fund == "n/a":
                if app_entry.customer_state == "CA":
                    template_values["message"] = "The customer did not qualify for Greensky, but we are checking HERO."

                funds = Helpers.list_funds()
                brake = False
                for fund in funds:
                    if brake:
                        continue
                    if fund["value"] == booking.fund:
                        if (cc.score >= fund["credit_floor_great"]) and (cc.score <= fund["credit_ceiling_great"]):
                            template_values["message"] = fund["match_message_great"]
                        elif (cc.score >= fund["credit_floor_good"]) and (cc.score <= fund["credit_ceiling_good"]):
                            template_values["message"] = fund["match_message_good"]

                        brake = True
            else:
                template_values["message"] = "The customer did not qualify for Greensky, but we are checking HERO."
        else:
            template_values["message"] = "The customer's credit check did not return useful results."
    path = Helpers.get_html_path('confirmation2.html')
    self.response.out.write(template.render(path, template_values))



