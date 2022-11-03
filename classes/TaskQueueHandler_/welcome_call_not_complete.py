def welcome_call_not_complete(self):
    notification = Notification.first(Notification.action_name == "Deal Closed but No Welcome Call Completed")
    if not notification is None:
        
        stats = LeaderBoardStat.query(
            ndb.AND(
                LeaderBoardStat.metric_key == "packets_submitted",
                LeaderBoardStat.dt >= Helpers.pacific_now() + timedelta(days=-14)
            )
        )
        app_ids_to_query = ["-1"]
        for stat in stats:
            app_ids_to_query.append(stat.field_app_identifier)

        pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.field_application_identifier.IN(app_ids_to_query))
        pp_sub_deal_closed_dict = {}
        app_ids_to_query2 = ["-1"]
        for pp_sub in pp_subs:
            if not pp_sub.archived and not pp_sub.save_me:
                app_ids_to_query2.append(pp_sub.field_application_identifier)
                result = False
                
                info = json.loads(pp_sub.extra_info)
                if "project_management_checkoffs" in info.keys():
                    if "welcome_call_completed" in info["project_management_checkoffs"].keys():
                        if "checked" in info["project_management_checkoffs"]["welcome_call_completed"].keys():
                            result = info["project_management_checkoffs"]["welcome_call_completed"]["checked"]

                pp_sub_deal_closed_dict[pp_sub.field_application_identifier] = result

        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query2))
        subject = "List of Deals Closed Without Welcome Calls"
        msg = "The following deals have been closed without a welcome call being completed:\r\n\r\n"
        cnt = 0
        for app_entry in app_entries:
            deal_closed = pp_sub_deal_closed_dict[app_entry.identifier]
            if not deal_closed:
                name = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
                rep_subject = "Deal Closed without a Welcome Call"
                Helpers.send_email(app_entry.rep_email, rep_subject, "The deal for " + name + " was marked as closed, but the welcome call has not been completed. Please do the welcome call as soon as possible.")
                msg += (name + "\r\n")
                cnt += 1

        if cnt > 0:
            for notification_person in notification.notification_list:
                Helpers.send_email(notification_person.email_address, subject, msg)

