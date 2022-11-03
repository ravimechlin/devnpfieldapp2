@staticmethod
def list_automatic_overrides():
    ret_dict = {}
    users = FieldApplicationUser.query(FieldApplicationUser.current_status == 0)
    usr_list = []
    for user in users:
        usr_list.append(user)

    usr_items = []
    for user in usr_list:
        usr_item = {}
        usr_item["name"] = user.first_name + " " + user.last_name
        usr_item["rep_id"] = user.rep_id
        usr_item["identifier"] = user.identifier
        usr_item["automatic_override_designee"] = user.automatic_override_designee
        usr_item["automatic_override_amount"] = user.automatic_override_amount
        usr_item["automatic_override_enabled"] = user.automatic_override_enabled

        usr_items.append(usr_item)

    return usr_items

