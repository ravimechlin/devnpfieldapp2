@staticmethod
def archive_state(identifier):
    from datetime import datetime
    for entity_results in [FieldApplicationEntry.query(FieldApplicationEntry.identifier == identifier),
                               SurveyBooking.query(SurveyBooking.field_app_identifier == identifier),
                               PerfectPacketEntry.query(PerfectPacketEntry.field_application_identifier == identifier),
                               PerfectPacketSubmission.query(PerfectPacketSubmission.field_application_identifier == identifier),
                               PerfectPacketApproval.query(PerfectPacketApproval.field_application_identifier == identifier),
                               CustomerProgressItem.query(CustomerProgressItem.field_app_identifier == identifier),
                               PayrollCustomerState.query(PayrollCustomerState.field_app_identifier == identifier),
                               Lead.query(Lead.field_app_identifier == identifier)]:
            for entity in entity_results:
                entity.archived = True
                entity.save_me = False
                entity.hold_items = "[]"
                entity.has_holds = False
                entity.put()

    reqd_actions = RepRequiredAction.query(RepRequiredAction.field_app_identifier == identifier)
    for a in reqd_actions:
        a.key.delete()

