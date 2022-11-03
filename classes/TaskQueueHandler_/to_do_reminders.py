def to_do_reminders(self):
    return
    now = Helpers.pacific_now()
    beginning = datetime(now.year, now.month, now.day, now.hour, 0, 0)
    end = datetime(now.year, now.month, now.day, now.hour, 59, 59)
    thirty_days_ago = now + timedelta(days=-30)

    to_dos = ToDoItem.query(
        ndb.AND(
            ToDoItem.reminder_dt >= beginning,
            ToDoItem.reminder_dt <= end
        )
    )

    to_dos2 = ToDoItem.query(ToDoItem.completed == False)

    to_do_identifier_name_dict = {}
    to_do_identifier_reminder_dt_dict = {}
    to_do_identifier_owner_dict = {}
    daily_reminders = []
    weekly_reminders = []
    monthly_reminders = []

    for to_do in to_dos2:
        to_do_identifier_name_dict[to_do.identifier] = to_do.name
        to_do_identifier_reminder_dt_dict[to_do.identifier] = to_do.reminder_dt
        to_do_identifier_owner_dict[to_do.identifier] = to_do.owner
        if to_do.daily_reminder and (not to_do.completed) and (to_do.reminder_dt.hour == now.hour):
            daily_reminders.append(to_do)
        if to_do.weekly_reminder and (not to_do.completed) and (now.isoweekday() == 1) and (now.hour == 9):
            weekly_reminders.append(to_do)
        if to_do.monthly_reminder and (not to_do.completed) and (now.day == 1) and (now.hour == 9):
            monthly_reminders.append(to_do)

    for to_do in to_dos:
        if (not to_do.reminder_sent) and (not to_do.completed):
            msg = "Reminding you about this item on your to-do list: " + to_do.name
            usr = FieldApplicationUser.first(
                ndb.AND(
                    FieldApplicationUser.identifier == to_do.owner,
                    FieldApplicationUser.current_status == 0
                )
            )
            if not usr is None:
                Helpers.send_sms(usr.rep_phone, msg)
            to_do.reminder_sent = True
            to_do.put()

    #daily recurring
    daily_keys_to_query = ["-1"]
    already_sent_daily = []
    for item in daily_reminders:
        daily_keys_to_query.append("daily_reminder_sent_" + item.identifier + "_" + str(now.date()))
        
    kv_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(daily_keys_to_query))
    for item in kv_items:
        already_sent_daily.append(item.keyy.split("_")[3])
    
    daily_kv_items_to_put = []
    for item in daily_reminders:
        if not item.identifier in already_sent_daily:
            msg = "Reminding you about this item on your to-do list: " + item.name
            usr = FieldApplicationUser.first(
                ndb.AND(
                    FieldApplicationUser.identifier == item.owner,
                    FieldApplicationUser.current_status == 0
                )
            )
            if not usr is None:
                Helpers.send_sms(usr.rep_phone, msg)
            kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="daily_reminder_sent_" + item.identifier + "_" + str(now.date()),
                val="1",
                expiration=now + timedelta(days=60)
            )
            daily_kv_items_to_put.append(kv)
    
    if len(daily_kv_items_to_put) == 1:
        daily_kv_items_to_put[0].put()
    elif len(daily_kv_items_to_put) > 1:
        ndb.put_multi(daily_kv_items_to_put)

    #weekly recurring
    weekly_keys_to_query = ["-1"]
    already_sent_weekly = []
    for item in weekly_reminders:
        weekly_keys_to_query.append("weekly_reminder_sent_" + item.identifier + "_" + str(now.date()))
        
    kv_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(weekly_keys_to_query))
    for item in kv_items:
        already_sent_weekly.append(item.keyy.split("_")[3])
    
    weekly_kv_items_to_put = []
    for item in weekly_reminders:
        if not item.identifier in already_sent_weekly:
            msg = "Reminding you about this item on your to-do list: " + item.name
            usr = FieldApplicationUser.first(
                ndb.AND(
                    FieldApplicationUser.identifier == item.owner,
                    FieldApplicationUser.current_status == 0
                )
            )
            if not usr is None:
                Helpers.send_sms(usr.rep_phone, msg)
            kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="weekly_reminder_sent_" + item.identifier + "_" + str(now.date()),
                val="1",
                expiration=now + timedelta(days=60)
            )
            weekly_kv_items_to_put.append(kv)
    
    if len(weekly_kv_items_to_put) == 1:
        weekly_kv_items_to_put[0].put()
    elif len(weekly_kv_items_to_put) > 1:
        ndb.put_multi(weekly_kv_items_to_put)

    #monthly recurring
    monthly_keys_to_query = ["-1"]
    already_sent_monthly = []
    for item in monthly_reminders:
        monthly_keys_to_query.append("monthly_reminder_sent_" + item.identifier + "_" + str(now.date()))
        
    kv_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(monthly_keys_to_query))
    for item in kv_items:
        already_sent_monthly.append(item.keyy.split("_")[3])
    
    monthly_kv_items_to_put = []
    for item in monthly_reminders:
        if not item.identifier in already_sent_monthly:
            msg = "Reminding you about this item on your to-do list: " + item.name
            usr = FieldApplicationUser.first(
                ndb.AND(
                    FieldApplicationUser.identifier == item.owner,
                    FieldApplicationUser.current_status == 0
                )
            )
            if not usr is None:
                Helpers.send_sms(usr.rep_phone, msg)
            kv = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy="monthly_reminder_sent_" + item.identifier + "_" + str(now.date()),
                val="1",
                expiration=now + timedelta(days=60)
            )
            monthly_kv_items_to_put.append(kv)
    
    if len(monthly_kv_items_to_put) == 1:
        monthly_kv_items_to_put[0].put()
    elif len(monthly_kv_items_to_put) > 1:
        ndb.put_multi(monthly_kv_items_to_put)

    to_dos3 = ToDoItem.query(ToDoItem.completed == True)
    for to_do in to_dos3:
        if to_do.completed_dt < thirty_days_ago:
            to_do.key.delete()

