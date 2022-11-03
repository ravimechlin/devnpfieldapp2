#composition based ndb classes come first
ndb_entity_names = ["PersonToNotify",
                    "SurveyBooking",
                    "SurveySlotBlock",
                    
                    "AuthKey",
                    "CalendarEvent",
                    "CheckPayment",
                    "ComposedDocument",
                    "ContestItem",
                    "CreditCheck",
                    "CustomerNote",
                    "CustomerProgressArchive",
                    "CustomerProgressItem",
                    "CustomerProgressV2Archive",
                    "CustomerProgressV2Item",
                    "CustomerProposalInfo",
                    "DeletedSurveyBooking",
                    "EmailTemplate",
                    "FieldApplicationEntry",
                    "FieldApplicationUser",
                    "HKTally",
                    "KeyValueStoreItem",
                    "LeaderBoardStat",
                    "Message",
                    "MessageThread",
                    "MonetaryTransaction",
                    "MonetaryTransactionV2",
                    "MonetaryTransactionV3",
                    "Notification",
                    "OfficeLocation",
                    "PanelAssessment",
                    "PayrollCustomerState",
                    "PendingAK",
                    "PerfectPacketApproval",
                    "PerfectPacketEntry",
                    "PerfectPacketSubmission",
                    "PinPoint",
                    "PlanSetDetails",
                    "PostalCampaignMessageV2",
                    "PowerUp",
                    "PowerUpSignOff",
                    "RepAssistance",
                    "Quiz",
                    "QuizQuestion",
                    "QuadrantAssignmentDetails",
                    "RepGoal",
                    "RepQuadrant",          
                    "RepRequiredAction",
                    "RoofWorkItem",
                    "ScheduledSMS",
                    "SheetDataItem",
                    "Slide",
                    "SlideItem",
                    "SlotDateException",
                    "Survey",                    
                    "SurveyDetails",
                    "SurveyQuestion",
                    "SurveyResponse",                                                                                                                                                             
                    "ThirdPartyFolder",
                    "ToDoItem",
                    "TrainingMedia",                                                                                                                        
                    "UserDebt",
                    "UserLocationLogItem",
                    "WhitePagesData",
                    "PinNote",
                    "Lead",
                    "OneOnOne",
                    "UserKnockedHours",
                    "KnockingMeeting",
                    "CustomerComm",
                    "SolarReader",
                    "PayrollCustomerStateV3",
                    "Runway",
                    "SuggestedKick",
                    "WeeklySurvey",
                    "PendingCDPayment"]
ndb_klass_definitions = []

cls_counter = 0

while cls_counter < len(ndb_entity_names):
    klass_definition = "class " + ndb_entity_names[cls_counter] + "(ndb.Model):\n"
    definition_lines = Helpers.get_ndb_class_definition_lines(ndb_entity_names[cls_counter])

    for definition_line in definition_lines:
        klass_definition += "\t" + definition_line + "\n"

    ndb_klass_definitions.append(klass_definition)

    cls_counter += 1

for ndb_klass_definition in ndb_klass_definitions:
    exec(ndb_klass_definition)

#class FieldApplicationEntry(ndb.Model):
    #identifier = ndb.StringProperty(required=True)
    #office_identifier = ndb.StringProperty(required=True)
    #booking_identifier = ndb.StringProperty(required=True)
    #shortened_identifier = ndb.ComputedProperty(lambda self: "p_" + str(zlib.crc32(self.identifier)).replace("-", "neg"))
    #customer_signature_date = ndb.DateProperty(required=True)
    #customer_first_name = ndb.StringProperty(required=True)
    #customer_last_name = ndb.StringProperty(required=True)
    #customer_email = ndb.StringProperty(required=True)
    #customer_phone = ndb.StringProperty(required=True)
    #customer_dob = ndb.DateProperty(required=True)
    #customer_postal = ndb.StringProperty(required=True)
    #customer_city = ndb.StringProperty(required=True)
    #customer_state = ndb.StringProperty(required=True)
    #customer_address = ndb.StringProperty(required=True)
    #customer_utility_account_number = ndb.StringProperty(required=True)
    #customer_kwh_price = ndb.StringProperty(required=True)
    #customer_cpf_id = ndb.IntegerProperty(required=True)

    #rep_id = ndb.StringProperty(required=True)
    #rep_email = ndb.StringProperty(required=True)
    #rep_phone = ndb.StringProperty(required=True)
    #rep_lead_id = ndb.StringProperty(required=True)

    #insert_time = ndb.IntegerProperty(required=True)
    #processed = ndb.IntegerProperty(required=True)
    #image_extension = ndb.StringProperty(required=True)


#class FieldApplicationUser(ndb.Model):
    #identifier = ndb.StringProperty(required=True)
    #first_name = ndb.StringProperty(required=True)
    #last_name = ndb.StringProperty(required=True)
    #main_office = ndb.StringProperty(required=True)
    #rep_id = ndb.StringProperty(required=True)
    #rep_email = ndb.StringProperty(required=True)
    #rep_phone = ndb.StringProperty(required=True)
    #user_type = ndb.StringProperty(required=True)
    #password = ndb.StringProperty(required=True)


#class SurveySlotBlock(ndb.Model):
    #identifier = ndb.StringProperty(required=True)
    #slot_1_enabled = ndb.BooleanProperty(required=True)
    #slot_2_enabled = ndb.BooleanProperty(required=True)
    #slot_3_enabled = ndb.BooleanProperty(required=True)
    #slot_4_enabled = ndb.BooleanProperty(required=True)
    #slot_5_enabled = ndb.BooleanProperty(required=True)
    #slot_6_enabled = ndb.BooleanProperty(required=True)
    #slot_7_enabled = ndb.BooleanProperty(required=True)
    #slot_8_enabled = ndb.BooleanProperty(required=True)
    #slot_9_enabled = ndb.BooleanProperty(required=True)
    #slot_10_enabled = ndb.BooleanProperty(required=True)
    #slot_11_enabled = ndb.BooleanProperty(required=True)
    #slot_12_enabled = ndb.BooleanProperty(required=True)


#class OfficeLocation(ndb.Model):
    #identifier = ndb.StringProperty(required=True)
    #name = ndb.StringProperty(required=True)
    #monday_slots = ndb.StructuredProperty(SurveySlotBlock)
    #tuesday_slots = ndb.StructuredProperty(SurveySlotBlock)
    #wednesday_slots = ndb.StructuredProperty(SurveySlotBlock)
    #thursday_slots = ndb.StructuredProperty(SurveySlotBlock)
    #friday_slots = ndb.StructuredProperty(SurveySlotBlock)
    #saturday_slots = ndb.StructuredProperty(SurveySlotBlock)
    #sunday_slots = ndb.StructuredProperty(SurveySlotBlock)


#class SlotDateException(ndb.Model):
    #identifier = ndb.StringProperty(required=True)
    #office_identifier = ndb.StringProperty(required=True)
    #exception_day = ndb.IntegerProperty(required=True)
    #exception_month = ndb.IntegerProperty(required=True)
    #exception_year = ndb.IntegerProperty(required=True)
    #slots = ndb.StructuredProperty(SurveySlotBlock)


#class SurveyBooking(ndb.Model):
    #identifier = ndb.StringProperty(required=True)
    #office_identifier = ndb.StringProperty(required=True)
    #field_app_identifier = ndb.StringProperty(required=True)
    #field_app_lead_id = ndb.StringProperty(required=True)
    #has_associated_field_entry = ndb.BooleanProperty(required=True)
    #slot_number = ndb.IntegerProperty(required=True)
    #booking_day = ndb.IntegerProperty(required=True)
    #booking_month = ndb.IntegerProperty(required=True)
    #booking_year = ndb.IntegerProperty(required=True)
    #address = ndb.StringProperty(required=True)
    #city = ndb.StringProperty(required=True)
    #state = ndb.StringProperty(required=True)
    #postal = ndb.StringProperty(required=True)
    #phone_number = ndb.StringProperty(required=True)
    #name = ndb.StringProperty(required=True)
    #email = ndb.StringProperty(required=True)
    #completion_state = ndb.IntegerProperty(required=True)
    #associated_rep_id = ndb.StringProperty(required=True)
    #utility_no = ndb.StringProperty(required=True)
    #notes = ndb.TextProperty(required=True)


#class DeletedSurveyBooking(ndb.Model):
    #identifier = ndb.StringProperty(required=True)
    #year = ndb.IntegerProperty(required=True)
    #bookings = ndb.StructuredProperty(SurveyBooking, repeated=True)


#class PersonToNotify(ndb.Model):
    #identifier = ndb.StringProperty(required=True)
    #email_address = ndb.StringProperty(required=True)


#class Notification(ndb.Model):
    #identifier = ndb.StringProperty(required=True)
    #action_name = ndb.StringProperty(required=True)
    #notification_list = ndb.StructuredProperty(PersonToNotify, repeated=True)

#actually commented out below....

#class SurveySlot(ndb.Model):
#    identifier = ndb.StringProperty(required=True)
#    lead_id = ndb.StringProperty(required=True)


#class SurveySlotContainers(ndb.Model):
#    identifier = ndb.StringProperty(required=True)
#    appt_month = ndb.IntegerProperty(required=True)
#    appt_day = ndb.IntegerProperty(required=True)
#    appt_year = ndb.IntegerProperty(required=True)
#    office_id = ndb.IntegerProperty(required=True)
#    slots = ndb.StructuredProperty(SurveySlot, repeated=True)
