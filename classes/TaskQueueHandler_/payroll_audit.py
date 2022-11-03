def payroll_audit(self):
    from datetime import datetime
    from datetime import date
    from google.appengine.api import app_identity

    pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.rep_submission_date >= (Helpers.pacific_now() + timedelta(days=-365)))
    thirty_days_ago = Helpers.pacific_now() + timedelta(days=-30)
    thirty_days_ago = thirty_days_ago.date()

    field_app_ids_1 = []
    for pp_sub in pp_subs:
        info = json.loads(pp_sub.extra_info)
        if "project_management_checkoffs" in info.keys():
            if "welcome_email_sent" in info["project_management_checkoffs"].keys():
                if "date" in info["project_management_checkoffs"]["welcome_email_sent"].keys():
                    if "checked" in info["project_management_checkoffs"]["welcome_email_sent"].keys():
                        if info["project_management_checkoffs"]["welcome_email_sent"]["checked"]:
                            dt_vals = info["project_management_checkoffs"]["welcome_email_sent"]["date"].split("-")
                            dt = date(int(dt_vals[0]), int(dt_vals[1]), int(dt_vals[2]))
                            if dt >= thirty_days_ago:
                                field_app_ids_1.append(pp_sub.field_application_identifier)

    if len(field_app_ids_1) > 0:        
        states_1 = PayrollCustomerState.query(
            ndb.AND(
                PayrollCustomerState.state_key == "welcome_call_completed",
                PayrollCustomerState.field_app_identifier.IN(field_app_ids_1)
            )
        )

        states_found_1 = []
        for state in states_1:
            states_found_1.append(state.field_app_identifier)

        transactions_found_1 = []
        transactions_1 = MonetaryTransactionV2.query(
            ndb.AND(
                MonetaryTransactionV2.description_key.IN(["rep_sales_commission_1A", "commission_miscellaneous_payout_A"]),
                MonetaryTransactionV2.field_app_identifier.IN(field_app_ids_1)
            )
        )
        for transaction in transactions_1:
            description = transaction.description
            if "First 50% of commission" in description and "Sold a" in description:
                transactions_found_1.append(transaction.field_app_identifier)

        unpaid_ids = []
        for app_id in field_app_ids_1:
            if (not app_id in states_found_1) and (not app_id in transactions_found_1):
                unpaid_ids.append(app_id)

        if len(unpaid_ids) > 0:
            app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(unpaid_ids))
            names = []
            for app_entry in app_entries:
                if (not app_entry.archived) and (not app_entry.save_me):
                    names.append(app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title())

            if len(names) > 0:
                subject = "Payroll Audit"
                msg = "The following customers reached welcome call complete and meet both of the following criteria:\r\nA. They do not currently appear in the payroll tab\r\nB. They have not been scheduled for payout.\r\n\r\nCustomers who meet this criteria:\r\n\r\n"
                msg += "\r\n".join(names)

                recip = "rnirnber@gmail.com"
                if app_identity.get_application_id() == "npfieldapp":
                    recip = "mcollins@newpower.net"

                Helpers.send_email(recip, subject, msg)


