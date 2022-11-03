@staticmethod
def get_points_for_deal(proposal):
    save = False
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "deal_points_" + proposal.field_app_identifier)
    ret = float(0)
    if not kv is None:
        ret = float(kv.val)
    else:
        save = True
        proposal.fix_additional_amount()
        prop_info = json.loads(proposal.info)
        existing_points = float(prop_info["all_points"])
        app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == proposal.field_app_identifier)
        if not app_entry is None:
            rep_id = app_entry.rep_id
            user = FieldApplicationUser.first(FieldApplicationUser.rep_id == rep_id)
            if not user is None:
                points_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "user_points_" + user.identifier)
                if not points_kv is None:
                    points_bank_value = float(points_kv.val)
                    if existing_points < float(0):
                        points_bank_value += (float(existing_points) * float(-1))
                        points_bank_value = round(points_bank_value, 2)
                        points_kv.val = str(points_bank_value)
                        points_kv.put()
                        ret = float(0)
                    elif existing_points > float(0) and points_bank_value > float(0):
                        while existing_points > float(0) and points_bank_value > float(0):
                            existing_points -= float(0.1)
                            existing_points = round(existing_points, 2)
                            points_bank_value -= float(0.1)
                            points_bank_value = round(points_bank_value, 2)
                        points_kv.val = str(points_bank_value)
                        points_kv.put()
                        ret = round(float(existing_points), 2)
                            
                    else:
                        ret = round(float(existing_points), 2)

    if save:
        kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="deal_points_" + proposal.field_app_identifier,
            val=str(ret),
            expiration=datetime(1970, 1, 1)
        )
        kv.put()
    return ret

