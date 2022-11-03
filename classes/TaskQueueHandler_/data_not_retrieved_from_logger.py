def data_not_retrieved_from_logger(self):
    from datetime import timedelta
 
    now = Helpers.pacific_now()
    thirty_minutes_ago = now + timedelta(minutes=-30)
    readers = SolarReader.query()

    for reader in readers:
        if not reader.field_app_identifier == "-1":
            if reader.deployment_dt.year > 1970:
                if reader.retrieval_dt.year == 1970:
                    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == reader.field_app_identifier)
                    if not app_entry is None:
                        if app_entry.sp_two_time < thirty_minutes_ago:
                            kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "data_not_retrieved_notification_sent_" + app_entry.identifier + "_" + str(app_entry.sp_two_time).split(".")[0])
                            if kv is None:
                                msg = "Data not Retrieved\n"
                                rep = FieldApplicationUser.first(FieldApplicationUser.identifier == reader.rep_ownership)
                                if not rep is None:
                                    msg += ("Responsible Party: " + rep.first_name.strip().title() + " " + rep.last_name.strip().title() + "\n")
                                    msg += ("Customer Name: " + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + "\n")
                                    msg += ("Appointment Time: " + str(app_entry.sp_two_time).split(".")[0])

                                    kv = KeyValueStoreItem(
                                        identifier=Helpers.guid(),
                                        keyy="data_not_retrieved_notification_sent_" + app_entry.identifier + "_" + str(app_entry.sp_two_time).split(".")[0],
                                        val="1",
                                        expiration=Helpers.pacific_now() + timedelta(days=14)
                                    )
                                    kv.put()

                                    notification = Notification.first(Notification.action_name == "Data Not Retrieved From Logger")
                                    if not notification is None:
                                        for p in notification.notification_list:
                                            Helpers.send_email(p.email_address, "Data Not Retrieved", msg)

