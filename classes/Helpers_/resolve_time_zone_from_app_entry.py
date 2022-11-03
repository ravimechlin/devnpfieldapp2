@staticmethod
def resolve_time_zone_from_app_entry(app_entry):
    dct = {"CA": "pacific_time", "CALIFORNIA": "pacific_time", "UT": "mountain_time", "UTAH": "mountain_time", "STOCKHOLM COUNTY": "central_european_time", "NY": "eastern_time", "NEW YORK": "eastern_time"}
    if app_entry.customer_state.upper() in dct.keys():
        return dct[app_entry.customer_state.upper()]
    return "pacific_time"

