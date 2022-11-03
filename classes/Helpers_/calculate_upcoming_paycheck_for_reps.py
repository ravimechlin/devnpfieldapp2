@staticmethod
def calculate_upcoming_paycheck_for_reps(rep_identifiers):
    ret_dict = {}
#    ret_dict["total"] = float("0.00")
    last_friday = Helpers.pacific_last_friday(int(Helpers.pacific_now().isoweekday() == 6))
    two_fridays_ago = last_friday + timedelta(days=-7)
    ret_dict["last_friday"] = str(last_friday)
    ret_dict["users"] = []
    ret_dict["transactions"] = []

    user_identifier_idx_dict = {}
    users = FieldApplicationUser.query(
        ndb.AND
        (
            FieldApplicationUser.user_type.IN(["field", "asst_mgr", "co_mgr", "sales_dist_mgr", "rg_mgr", "solar_pro" "solar_pro_manager", "energy_expert", "sales_manager"]),
            FieldApplicationUser.current_status == 0
        )
    ).order(FieldApplicationUser.first_name).order(FieldApplicationUser.last_name)
    cnt = 0
    for user in users:
        user_item = {}
        user_item["identifier"] = user.identifier
        user_item["rep_id"] = user.rep_id
        user_item["first_name"] = user.first_name
        user_item["last_name"] = user.last_name
        user_item["transactions"] = []

        ret_dict["users"].append(user_item)

        user_identifier_idx_dict[user.identifier] = cnt

        cnt += 1


    transactions = MonetaryTransaction.query(
        ndb.AND
        (
            MonetaryTransaction.recipient.IN(rep_identifiers),
            MonetaryTransaction.effective_dt < last_friday,
            MonetaryTransaction.approved == True,
            MonetaryTransaction.denied == False
        )
    ).order(MonetaryTransaction.effective_dt)

    monetary_transactions_cpy = []
    for transaction in transactions:
        if transaction.effective_dt > two_fridays_ago:
            monetary_transactions_cpy.append(transaction)

    done = False
    while not done:
        items_found_out_of_order = False
        count = 0
        while count < len(monetary_transactions_cpy):
            this_date = monetary_transactions_cpy[count].recorded_dt
            this_effective_date = monetary_transactions_cpy[count].effective_dt
            has_prev_date = (not count == 0)
            if has_prev_date:
                prev_date = monetary_transactions_cpy[count - 1].recorded_dt
                prev_effective_date = monetary_transactions_cpy[count - 1].effective_dt
                if this_date < prev_date:
                    if this_effective_date < prev_effective_date:
                        lst = []
                        lst.append(monetary_transactions_cpy[count])
                        lst.append(monetary_transactions_cpy[count - 1])
                        monetary_transactions_cpy[count] = lst[1]
                        monetary_transactions_cpy[count - 1] = lst[0]
                        count = len(monetary_transactions_cpy)
                        items_found_out_of_order = True

            count += 1

        done = not items_found_out_of_order


    for transaction in monetary_transactions_cpy:
        transaction_item = {}
        transaction_item["identifier"] = transaction.identifier
        transaction_item["amount"] = (transaction.dollars * 100) + transaction.cents
        transaction_item["description"] = transaction.description
        transaction_item["recorded"] = str(transaction.recorded_dt)
        transaction_item["effective"] = str(transaction.effective_dt)
        transaction_item["check_number"] = transaction.check_number

        ret_dict["users"][user_identifier_idx_dict[transaction.recipient]]["transactions"].append(transaction_item)

        ret_dict["transactions"].append(transaction_item)

    copied_users = []
    ret_dict["positive_user_list"] = []
    for usr in ret_dict["users"]:
        if len(usr["transactions"]) > 0:
            copied_users.append(usr)
            ret_dict["positive_user_list"].append(usr["identifier"])

    check_num_keys = ["-1"]
    paid_status_keys = ["-1"]
    noww = Helpers.pacific_now()
    wd = noww.isoweekday()
    while (not wd == 5):
        noww = noww + timedelta(days=1)
        wd = noww.isoweekday()

    this_upcoming_friday = noww

    for usr in copied_users:
        check_num_keys.append("check_number_for_" + usr["identifier"] + "_" + str(this_upcoming_friday).split(" ")[0])

    for usr in copied_users:
        paid_status_keys.append("check_paid_for_" + usr["identifier"] + "_" + str(this_upcoming_friday).split(" ")[0])

    check_num_keys_cpy = []
    kv_items1 = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(check_num_keys))
    for kv_item1 in kv_items1:
        keyyyyyyyy = kv_item1.keyy.replace("check_number_for_", "").split("_")[0]
        check_num_keys_cpy.append(keyyyyyyyy)

    paid_status_keys_cpy = []
    kv_items2 = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(paid_status_keys))
    for kv_item2 in kv_items2:
        keyyyyyyyy = kv_item2.keyy.replace("check_paid_for_", "").split("_")[0]
        paid_status_keys_cpy.append(keyyyyyyyy)

    ret_dict["check_status_map"] = {}

    for usr in copied_users:
        status = 0

        try:
            idx1 = paid_status_keys_cpy.index(usr["identifier"])
            status = 2
        except:
            try:
                idx2 = check_num_keys_cpy.index(usr["identifier"])
                status = 1
            except:
                status = status

        ret_dict["check_status_map"][usr["identifier"]] = status

    ret_dict["users"] = copied_users


    return ret_dict
