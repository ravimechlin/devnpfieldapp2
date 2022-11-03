@staticmethod
def get_customer_presentation_variables(app_entry):
    ret = {}
    ret["cust_first"] = app_entry.customer_first_name.strip().title()
    ret["cust_last"] = app_entry.customer_last_name.strip().title()
    ret["cust_name"] = ret["cust_first"] + " " + ret["cust_last"]
    ret["cust_city"] = app_entry.customer_city.strip().title()
    ret["cust_state"] = app_entry.customer_state.upper()
    ret["cust_address"] = app_entry.customer_address.strip().title()
    ret["cust_postal"] = app_entry.customer_postal
    ret["highest_monthly_bill"] = Helpers.currency_format(app_entry.highest_amount).replace("$", "").replace(",", "")
    ret["annual_electric_bill"] = Helpers.currency_format(app_entry.total_dollars).replace("$", "").replace(",", "")
    ret["annual_kilowatts_used"] = Helpers.currency_format(app_entry.total_kwhs).replace("$", "").replace(",", "")
    ret["average_bill"] = Helpers.currency_format(float(ret["annual_electric_bill"]) / float(12)).replace("$", "").replace(",", "")
    ret["thirty_year_utility_cost"] = "0.00"
    ret["current_avg_cost_per_kwh"] = Helpers.currency_format(float(app_entry.total_dollars) / float(app_entry.total_kwhs)).replace("$", "").replace(",", "")
    ret["federal_tax_credit"] = "0.00",
    ret["estimated_bill_in_30_years"] = "0.00"
    ret["user_input_1"] = ""
    ret["user_input_2"] = ""
    ret["user_input_3"] = ""
    ret["user_input_4"] = ""
    ret["user_input_5"] = ""
    ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
    if not ol is None:
        booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
        if not booking is None:
            proposal = CustomerProposalInfo.first(CustomerProposalInfo.field_app_identifier == app_entry.identifier)
            if not proposal is None:
                proposal.fix_additional_amount()
                proposal.fix_system_size()
                info = json.loads(proposal.info)
                structures = Helpers.get_pricing_structures()
                funds = Helpers.list_funds()
                ret["thirty_year_utility_cost"] = Helpers.currency_format(Helpers.crunch("fx_30_Year_Utility_Cost", ol.parent_identifier, app_entry, booking, info, structures, funds)).replace("$", "").replace(",", "")
                ret["federal_tax_credit"] = Helpers.currency_format(Helpers.crunch("fx_Federal_Tax_Credit", ol.parent_identifier, app_entry, booking, info, structures, funds)).replace("$", "").replace(",", "")
                ret["estimated_bill_in_30_years"] = Helpers.currency_format(Helpers.crunch("fx_Utility_Bill_In_30_Years", ol.parent_identifier, app_entry, booking, info, structures, funds)).replace("$", "").replace(",", "")

                formula_list = Helpers.list_crunchable_fns()
                for f in formula_list:
                    result = Helpers.crunch(f, ol.parent_identifier, app_entry, booking, info, structures, funds)
                    try:
                        ret[f] = Helpers.currency_format(result).replace("$", "").replace(",", "")
                    except:
                        ret[f] = str(result)
    return ret
