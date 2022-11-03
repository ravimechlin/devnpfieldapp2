@staticmethod
def get_surveyor_checklist_identifier():
    surveys = Survey.query(Survey.active_triggers == "{\"survey\":[\"before_surveyor_updates_status_in_view\"]}")
    identifier = None
    for survey in surveys:
        identifier = survey.identifier

    return identifier

