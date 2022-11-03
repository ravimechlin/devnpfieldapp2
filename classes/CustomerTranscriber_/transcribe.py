
"""Transcribe class has methods to add messages for a customer."""
@staticmethod
def transcribe(app_entry=None, user=None, key=None, blob_count=0, utc_dt=None, pacific_dt=None):
    if utc_dt is None:
        utc_dt = datetime.now()

    if pacific_dt is None:
        pacific_dt = Helpers.pacific_now()

    """Add a message by key."""
    if app_entry is None:
        logging.error("A FieldApplicationEntry object is required to post a message")
        return None
    if user is None:
        logging.error("A user is required to post a message")
        return None
    if key is None:
        logging.error("A key is required to post a message")
        return None

    #pt_now = Helpers.pacific_now()
    #pt_sans_microseconds = datetime(pt_now.year, pt_now.month, pt_now.day, pt_now.hour, pt_now.minute, pt_now.second)
    #friendly_date_str = str(pt_sans_microseconds)

    cust_name = "{cust_name}"
    cust_name = app_entry.customer_first_name + " " + app_entry.customer_last_name
    
    # get the reps name on the order
    reps_name = "{Missing}"
    rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
    if rep is not None:
        reps_name = rep.first_name + " " + rep.last_name

    # get the name of the current user logged who posted this
    curr_reps_name = "{System}"
    curr_rep = user
    if curr_rep is not None:
        curr_reps_name = curr_rep.first_name + " " + curr_rep.last_name

    office_name = "{Missing}"
    office = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
    if not office is None:
        office_name = office.name

    # generate the message
    # need a contest reject of pp and need reasons why the rep thinks it should no longer be rejected
    # survey_status_update - integer reflecting status is outside this function. If cancelled it will show why in the post.
    # trust docs may be backwards no means yes (maybe)
    # booking cancellations happen in the upcoming view
    # approving the packet is synonomous with pending approval
    #   txt = "Perfect Packet was complete for {} by {}".format(cust_name, curr_reps_name)
    #   txt = "Perfect Packet was complete for " + cust_name + " by " + curr_reps_name

    txt = None
    if key == "sales_form_post":
        txt = cust_name + "'s information was entered into the database by " + reps_name + ". The lead was generated from the " + office_name + " office."
    elif key == "sp2_set":
        txt = "An SP2 appointment was scheduled for " + app_entry.sp_two_time.strftime("%Y-%m-%d %I:%M %p") + "."
    elif key == "survey_booked":
        booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
        survey_date_str = ""
        if not booking is None:
            survey_date_str = datetime(booking.booking_year, booking.booking_month, booking.booking_day).strftime("%Y-%m-%d")
            booking_slot_str = str(booking.slot_number)
        txt = "Survey was booked for " + survey_date_str + " at slot position #" + booking_slot_str + " for the " + office_name + " office."
    elif key == "crm_work_cpf":
        txt = cust_name + " was entered into Clean Power Finance."
    elif key == "crm_work_mosaic":
        txt = cust_name + " was entered into Mosaic."
    elif key == "fund_set":
        booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
        fund_name = "{Missing}"
        funds = Helpers.list_funds()
        if not booking is None:
            for f in funds:
                if f["value"] == booking.fund:
                    fund_name = f["value_friendly"]

        txt = "The fund was updated to " + fund_name + "."
    elif key == "trust_docs":
        booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
        txt = "Trust docs for " + cust_name + " were marked."
        trust_docs_val_set = {"n/a": "Not Sure", "yes": "Not Required", "no": "Required"}
        if not booking is None:
            txt = "Trust docs for " + cust_name + " were marked as \"" + trust_docs_val_set[booking.trust_docs] + "\"."
    elif key == "booking_cancelled":
        txt = "The survey appointment for " + cust_name + " was cancelled."
    elif key == "survey_status_update":
        txt = "The surveyor provided a status update of {cust_name}'s survey: {missing}."
        try:
            booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
            booking_status_list = ["", "Partial", "Completed", "Cancelled"]
            txt = "The surveyor provided a status update for " + cust_name + "'s survey: " + booking_status_list[booking.completion_state] + "."
        except:
            txt = txt

    elif key == "installation_date_set":
        txt = "An installation date for " + cust_name + " was set for {date}"
        pp_sub = PerfectPacketSubmission.first(PerfectPacketSubmission.field_application_identifier == app_entry.identifier)
        if not pp_sub is None:
            pp_info = json.loads(pp_sub.extra_info)
            if "installation_date" in pp_info.keys():
                txt = txt.replace("{date}", pp_info["installation_date"])

    elif key == "plan_set_requested":
        txt = "The plan set was requested."
    elif key == "plan_set_received":
        txt = "The plan set was received."
    elif key == "stamps_received":
        txt = "The stamps were received."
    elif key == "pp_sub":
        txt = "A packet for {cust_name} was created for {curr_reps_name} to complete."
    elif key == "complete_perfect_packet":
        txt = "{curr_reps_name} submitted " + cust_name + "'s Perfect Packet for approval."
    elif key == "pp_rejected_pending_resubmission":
        txt = "The packet for " + cust_name + " was rejected."
    elif key == "contest_rejection":
        txt = "{rep_name} resubmitted {cust_name}'s packet for reapproval."
    elif key == "approve_perfect_packet":
        txt = cust_name + " reached Perfect Packet Approval. Approval date: "
        pp_approval = PerfectPacketApproval.first(PerfectPacketApproval.field_application_identifier == app_entry.identifier)
        if not pp_approval is None:
            txt += (pp_approval.approval_date.strftime("%Y-%m-%d") + ".")
        else:
            txt += "{Missing}."
    elif key == "pending_perm_approved":
        pending_perm_approved_dt_str = "{Missing}"
        archive = CustomerProgressArchive.first(
            ndb.AND
            (
                CustomerProgressArchive.field_app_identifier == app_entry.identifier,
                CustomerProgressArchive.step_key == "pending_perm_approved"
            )
        )
        if not archive is None:
            pending_perm_approved_dt_str = archive.updated.strftime("%Y-%m-%d")
        txt = cust_name + " is waiting for permit approval from the city. The permit was submitted on: "
        if archive is None:
            txt += "{Missing}."
        else:
            txt += (pending_perm_approved_dt_str + ".")
    elif key == "perm_rejected_pending_resubmission":
        archive = CustomerProgressArchive.first(
            ndb.AND
            (
                CustomerProgressArchive.field_app_identifier == app_entry.identifier,
                CustomerProgressArchive.step_key == "perm_rejected_pending_resubmission"
            )
        )
        txt = cust_name + "'s permit was initially rejected, and is pending another resubmission."
        if not archive is None:
            txt += " The rejection date was " + archive.updated.strftime("%Y-%m-%d") + "."

    elif key == "perm_approved_pending_scheduling":
        txt = cust_name + "'s permit was approved and is currently pending scheduling."
        archive = CustomerProgressArchive.first(
            ndb.AND
            (
                CustomerProgressArchive.field_app_identifier == app_entry.identifier,
                CustomerProgressArchive.step_key == "perm_approved_pending_scheduling"
            )
        )
        if not archive is None:
            txt += " The approval date was " + archive.updated.strftime("%Y-%m-%d") + "."
    elif key == "panel_work_needed":
        txt = cust_name + "'s permit was approved with panel work being required."
        archive = CustomerProgressArchive.first(
            ndb.AND
            (
                CustomerProgressArchive.field_app_identifier == app_entry.identifier,
                CustomerProgressArchive.step_key == "perm_approved_pending_scheduling"
            )
        )
        if not archive is None:
            txt += " This determination was made on: " + archive.updated.strftime("%Y-%m-%d") + "."

    elif key == "panel_work_scheduled":
        panel_work_scheduled_dt_str = "{Missing}"
        archive = CustomerProgressArchive.first(
            ndb.AND
            (
                CustomerProgressArchive.field_app_identifier == app_entry.identifier,
                CustomerProgressArchive.step_key == "panel_work_scheduled"
            )
        )
        if not archive is None:
            panel_work_scheduled_dt_str = archive.updated.strftime("%Y-%m-%d")
        txt = cust_name + "'s panel work is scheduled for the following date: " + panel_work_scheduled_dt_str + "."
    elif key == "construction_start_scheduled":
        txt = "{cust_name} is scheduled for construction complete."
        archive = CustomerProgressArchive.first(
            ndb.AND
            (
                CustomerProgressArchive.field_app_identifier == app_entry.identifier,
                CustomerProgressArchive.step_key == "construction_start_scheduled"
            )
        )
        if not archive is None:
            txt += " The date for construction start is: " + archive.updated.strftime("%Y-%m-%d") + "."
    elif key == "construction_completed":
        txt = "Construction was completed for {cust_name}. "
        archive = CustomerProgressArchive.first(
            ndb.AND
            (
                CustomerProgressArchive.field_app_identifier == app_entry.identifier,
                CustomerProgressArchive.step_key == "construction_completed"
            )
        )
        if not archive is None:
            txt += ("The completion date was recorded as happening on " + archive.updated.strftim("%Y-%m-%d") + ".")
    elif key == "operation_perm":
        txt = "Permission to operate was granted for " + cust_name + "."
        archive = CustomerProgressArchive.first(
            ndb.AND
            (
                CustomerProgressArchive.field_app_identifier == app_entry.identifier,
                CustomerProgressArchive.step_key == "operation_perm"
            )
        )
        if not archive is None:
            txt += (" Permission was granted " + archive.updated.strftime("%Y-%m-%d") + ".")
    elif key == "rep_sp2_reschedule_inhouse":
        txt = "An SP2 appointment was rescheduled between with an appointment time of " + app_entry.sp_two_time.strftime("%Y-%m-%d %I:%M %p") + "."
    elif key == "set_holds_for_customer":
        try:
            holds = json.loads(app_entry.hold_items)
            counter = 0
            hold_txt = ""
            for item in holds:
                counter += 1
                hold_txt += " {}) {}".format(counter, item)
        except:
            hold_txt = ""
        txt = "A hold was placed on {}. Reasons: {}".format(cust_name, hold_txt)
    elif key == "release_holds":
        txt = "A hold was released for {}".format(cust_name)
    elif key == "customer_archived":
        txt = cust_name + " was placed into archive."
    elif key == "customer_unarchived":
        txt = cust_name + " was removed from the archive."
    elif key == "customer_save_me_annotation":
        txt = cust_name + " was marked as \"Save Me\""
    elif key == "customer_remove_save_me_annotation":
        txt = "Hooray!" + cust_name + " was saved!"
    elif key == "customer_save_me_archive_autopurge":
        txt = cust_name + " was automatically archived after being in save me for more than two weeks."
    elif key == "usage_info_updated":
        txt = "An admin has updated usage info for " + cust_name + "."
    elif key == "proposal_updated":
        proposal = CustomerProposalInfo.first(CustomerProposalInfo.field_app_identifier == app_entry.identifier)
        if not proposal is None:
            proposal.fix_system_size()
            txt = "A proposal was submitted for " + cust_name + ". The new system size is " + str(json.loads(proposal.info)["system_size"]) + "."
    elif key == "new_survey_cancel":
        txt = "The survey for " + cust_name + " was cancelled. An email was sent out to the rep explaining the reason."
    elif key == "new_survey_complete_with_signature_request":
        txt = "The survey for " + cust_name + " was completed. However, a new layout signature was marked as required."
    elif key == "new_survey_complete":
        txt = "The survey for " + cust_name + " was completed."
    elif key == "electrical_completed":
        txt = "Electrical/Panel Work for " + cust_name + " was marked as completed."
    elif key == "tier_option_update":
        txt = "The commission option for " + cust_name + " was set to 'tier " + app_entry.tier_option + "'."
    elif key == "panel_qty_update":
        proposal = CustomerProposalInfo.first(CustomerProposalInfo.field_app_identifier == app_entry.identifier)
        if not proposal is None:
            proposal.fix_system_size()
            txt = "The panel quantity for " + cust_name + " was updated. The new system size is " + str(json.loads(proposal.info)["system_size"]) + "."
    elif key == "customer_signs_docs_start":
        txt = cust_name + " signed docs. A job was kicked off to save these documents in Google Drive."
    elif key == "customer_signs_docs_end":
        txt = cust_name + "'s signed documents were saved into Google Drive."

    elif key == "deal_closed":
        txt = "The deal for " + cust_name + " was marked as 'closed'."
    elif key == "customer_office_reassignment":
        ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
        if not ol is None:
            txt = cust_name + " was reassigned to the '" + ol.name + "' office."
    else:
        pass

    if txt is None:
        logging.info(("{0} is not a valid key to post a message").format(key))
        note_id = None
    else:
        note = None
        designee = None
        note_id = Helpers.guid()
        try:
            note = CustomerNote(
                identifier=note_id,
                field_app_identifier=app_entry.identifier,
                inserted_pacific=pacific_dt,
                inserted_utc=utc_dt,
                author=user.identifier,
                perms="public",
                content=json.dumps({"txt": [txt]}),
                blob_count=blob_count,
                note_key=key,
                read=False
            )
            designee = note.get_designee()
            note.read = False
            note.put()

        except:
            exctype, value = sys.exc_info()[:2]
            logging.error("note put error({0}): {1} while putting ({2}): '{3}'".format(exctype, value, key, txt))
            note_id = None

        if (not note is None) and (not designee is None):
            f = GCSLockedFile("/ApplicationSettings/UserSettings/Notifications/" + rep.identifier + ".json")
            content = f.read()
            if not content is None:
                settings = json.loads(content)
                if "new_customer_note" in settings.keys():
                    if settings["new_customer_note"]["sms"] == True:
                        try:
                            msg = "a new note for one of your customers (" + app_entry.customer_first_name.strip() + " " + app_entry.customer_last_name.strip() + ") got recorded in the field app."
                            #Helpers.send_sms(rep.rep_phone, msg)
                        except:
                            logging.error("SMS failed")
                    if settings["new_customer_note"]["email"] == True:
                        try:
                            msg2 = rep.first_name.strip() + " " + rep.last_name.strip() + ",\n\nA new note for " + app_entry.customer_first_name.strip() + " " + app_entry.customer_last_name.strip() + " was recorded:\n\n\"" + note.content + "\""
                            #Helpers.send_email(rep.rep_email, "New Customer Note!", msg2)
                        except:
                            logging.error("Customer note notification failed")


    return note_id

