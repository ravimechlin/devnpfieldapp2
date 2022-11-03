@staticmethod
def save_me_state(app_entry, reason):
    identifier = app_entry.identifier
    items = [
        FieldApplicationEntry.first(FieldApplicationEntry.identifier == identifier),
        SurveyBooking.first(SurveyBooking.field_app_identifier == identifier),
        CustomerProgressItem.first(CustomerProgressItem.field_app_identifier == identifier),
        PerfectPacketEntry.first(PerfectPacketEntry.field_application_identifier == identifier),
        PerfectPacketSubmission.first(PerfectPacketSubmission.field_application_identifier == identifier),
        PerfectPacketApproval.first(PerfectPacketApproval.field_application_identifier == identifier),
        PayrollCustomerState.first(PayrollCustomerState.field_app_identifier == identifier),
        Lead.first(Lead.field_app_identifier == identifier)
    ]

    items_to_put = []
    cnt = 0
    for item in items:
        if not item is None:
            item.save_me = True
            item.archived = False

            if cnt == 0:
                item.save_me_reason = reason
                item.save_me_dt = Helpers.pacific_now()

            items_to_put.append(item)

        cnt += 1

    if len(items_to_put) == 1:
        items_to_put[0].put()
    else:
        ndb.put_multi(items_to_put)


    msg = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + " is trying to cancel. Please find the account in your save me icon and try to save him/her. Supposed Reason for cancellation:\n\n" + reason
    try:
        Helpers.send_email(app_entry.rep_email, "Save this customer!", msg)
        if not app_entry.lead_generator == "-1":
            solar_pro = FieldApplicationUser.first(FieldApplicationUser.identifier == app_entry.lead_generator)
            if not solar_pro is None:
                x = 5
                #Helpers.send_email(solar_pro.rep_email, "Save this customer!", msg)
    except:
        msg = msg
    usr = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
    if not usr is None:
        try:
            CustomerTranscriber.transcribe(app_entry, usr, "customer_save_me_annotation")
        except:
            usr = usr

        msg = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + " is marked as a potential cancel."
        Helpers.send_sms(usr.rep_phone, msg)

    reqd_actions = RepRequiredAction.query(RepRequiredAction.field_app_identifier == identifier)
    for a in reqd_actions:
        a.key.delete()

    notification = Notification.first(Notification.action_name == "Save Me State")
    for person in notification.notification_list:
        Helpers.send_email(person.email_address, "Customer is trying to cancel", app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + "\r\n\r\nReason:\r\n:" + reason)

    
    old_event_start_dt_dict = {"final_inspection": "2001-01-01 00:00:00", "install": "2001-01-01 00:00:00", "permit_to_city": "2001-01-01 00:00:00"}
    old_event_end_dt_dict = {"final_inspection": "2001-01-01 01:00:00", "install": "2001-01-01 01:00:00", "permit_to_city": "2001-01-01 01:00:00"}
    events = CalendarEvent.query(
        ndb.AND(
            CalendarEvent.field_app_identifier == identifier,
            CalendarEvent.event_key.IN(["final_inspection", "install", "permit_to_city"])
        )
    )
    for event in events:
        old_start_dt = event.start_dt
        old_end_dt = event.end_dt
        old_start_dt_str = str(old_start_dt.year) + "_" + str(old_start_dt.month) + "_" + str(old_start_dt.day) + "_" + str(old_start_dt.hour) + "_" + str(old_start_dt.minute) + "_" + str(old_start_dt.second)
        old_end_dt_str = str(old_end_dt.year) + "_" + str(old_end_dt.month) + "_" + str(old_end_dt.day) + "_" + str(old_end_dt.hour) + "_" + str(old_end_dt.minute) + "_" + str(old_end_dt.second)
        
        old_event_start_dt_dict[event.event_key] = str(event.start_dt)
        old_event_end_dt_dict[event.event_key] = str(event.end_dt)
        event.start_dt = datetime(2001, 1, 1, 0, 0, 0)
        event.end_dt = datetime(2001, 1, 1, 1, 0, 0)
        event.put()

        #from google.appengine.api import taskqueue
        #taskqueue.add(url="/tq/google_calendar", params={"identifier": event.identifier, "fn": "update_one_time_event", "old_start_dt": old_start_dt_str, "old_end_dt": old_end_dt_str})
        from google.appengine.api import taskqueue
        taskqueue.add(url="/tq/google_calendar", params={"fn": "delete_one_time_event", "identifier": event.identifier, "old_start_dt": old_start_dt_str, "old_end_dt": old_end_dt_str})

    kv = KeyValueStoreItem(
        identifier=Helpers.guid(),
        keyy="save_me_events_" + identifier,
        val=json.dumps({"start": old_event_start_dt_dict, "end": old_event_end_dt_dict}),
        expiration=datetime(1970, 1, 1)
    )
    kv.put()

