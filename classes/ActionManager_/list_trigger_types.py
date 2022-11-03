@staticmethod
def list_trigger_types():
    ret_dict = {}
    ret_dict["field"] = {}

    ret_dict["field"]["before_rep_completes_survey"] = "Before Field Rep Completes Survey"
    ret_dict["field"]["after_rep_completes_survey"] = "After Field Rep Completes Survey"
    ret_dict["field"]["after_rep_completes_sp2"] = "After Field Rep Completes SP2 Appointment"

    ret_dict["survey"] = {}


    ret_dict["survey"]["before_surveyor_updates_status_in_view"] = "Before Surveyor Provides Status Update"
    ret_dict["survey"]["after_surveyor_updates_status_in_view"] = "After Surveyor Provides Status Update"

    return ret_dict

