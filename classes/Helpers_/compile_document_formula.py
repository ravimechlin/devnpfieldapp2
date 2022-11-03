@staticmethod
def compile_document_formula(formula_str, rep_employment_docs_mode=False):
    replacements = [
        [
            "IN [",
            "in ["
        ],
        [
            "AND",
            "and",
        ],
        [
            "OR",
            "or"
        ],
        [
            "NOT",
            "not"
        ],
        [
            "cstPostal",
            "app_entry.customer_postal"
        ],
        [
            "cstCounty",
            "app_entry.customer_county"
        ],
        [
            "cstState",
            "app_entry.customer_state"
        ],
        [
            "supplementaryFund",
            "booking.secondary_fund"
        ],
        [
            "reroofType",
            "app_entry.reroof_type"
        ],
        [
            "reroofDocType",
            "app_entry.reroof_doc_type"
        ],
        [
            "cstFund",
            "booking.fund"
        ],
        [
            "cstUtility",
            "app_entry.utility_provider"
        ],
        [
            "cstMarket",
            "market.identifier"
        ],
        [
            "usrState",
            "pending_user[\"user_primary_state\"].upper()"
        ],
        [
            "usrType",
            "pending_user[\"user_type\"]"
        ],
        [
            "salesRep",
            "field"
        ],
        [
            "asstManager",
            "asst_mgr"
        ],
        [
            "coManager",
            "co_mgr"
        ],
        [
            "salesDistrictManager",
            "sales_dist_mgr"
        ],
        [
            "regionalManager",
            "rg_mgr"
        ],
        [
            "W2Employee",
            "super"
        ],
        [
            "solarProManager",
            "solar_pro_manager"
        ],
        [
            "solarPro",
            "solar_pro"
        ],
        [
            "energyExpert",
            "energy_expert"
        ],
        [
            "salesManager",
            "sales_manager"
        ],
        [
            "=",
            "=="
        ]
    ]
    for replacement in replacements:
        formula_str = formula_str.replace(replacement[0], replacement[1])

    if rep_employment_docs_mode:
        formula_str = "lambda pending_user: " + formula_str
    else:
        formula_str = "lambda app_entry, booking, proposal, market: " + formula_str
    return {"source": formula_str, "fn": eval(formula_str)}
