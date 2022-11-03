@staticmethod
def compile_formula(formula_key, formulas=None):

    #lookup the formulas
    if formulas is None:
        formulas = Helpers.read_setting("proposal_formulas")
    idx_check = None
    try:
        idx_check = formulas[formula_key].index("|||")
    except:
        idx_check = idx_check
    if formula_key in formulas.keys() and (not formulas[formula_key].strip() == "") and (not idx_check == 0):
        definition = formulas[formula_key]
        if "|||" in definition:
            definition = definition.split("|||")[0]

        while "fx_" in definition:
            for key in formulas.keys():
                if not "fx_" in definition:
                    continue
                reference_def = formulas[key].strip()
                if "|||" in reference_def:
                    reference_def = reference_def.split("|||")[0]

                definition = definition.replace(key, " (" + reference_def + ") ")
                definition = definition.replace("   ", " ")
                definition = definition.replace("  ", " ")
                definition = definition.strip()

        var_dict = {
            "SS": "float(proposal_dict[\"system_size\"])",
            "HMB": "app_entry.highest_amount",
            "TKWHRS": "app_entry.total_kwhs",
            "TD": "app_entry.total_dollars",
            "UM": "float(app_entry.usage_months)",
            "ADDCST": "float(proposal_dict[\"additional_amount\"])",
            "stCA": "float(int(app_entry.customer_state == 'CA'))",
            "stUT": "float(int(app_entry.customer_state == 'UT'))",
            "tierA": "float(int(app_entry.tier_option == 'A'))",
            "tierB": "float(int(app_entry.tier_option == 'B'))",
            "tierC": "float(int(app_entry.tier_option == 'C'))",
            "tierD": "float(int(app_entry.tier_option == 'D'))",
            "tierE": "float(int(app_entry.tier_option == 'E'))"
        }

        funds = Helpers.list_funds()
        for fund in funds:
            var_dict["fnd" + Helpers.constanticize(fund["value"])] = "float(int(booking.fund == '" + fund["value"] + "'))"

        for var in var_dict.keys():
            val = var_dict[var]

            if var in definition:
                definition = definition.replace(var, val)

        definition = definition.replace("AND", "and").replace("OR", "or").replace("NOT", "").replace("^", "**")
        while "  " in definition:
            definition = definition.replace("  ", " ")


        if formula_key == "fx_State_Tax_Credit":
            definition = "(" + definition + ") * int(not (app_entry.customer_postal[0] == \"7\"))"
            
        return {"source": definition, "fn": eval("lambda app_entry, booking, proposal_dict: " + definition)}

    else:
        return None


