def remind_assistance_needed(self):
    items = RepAssistance.query()
    for item in items:
        rep = FieldApplicationUser.first(FieldApplicationUser.identifier == item.rep_identifier)
        if not rep is None:
            app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == item.field_app_identifier)
            if not app_entry is None:
                msg = "Hey " + rep.first_name.strip().title() + " " + rep.last_name.strip().title() + ",\r\n\r\n"
                msg = msg + "You have some outstanding items to complete for customer " + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + ". Please login to the field app and click on rep assist to view. If these items are not completed soon, the project will be cancelled."
                Helpers.send_sms(rep.rep_phone, msg)

