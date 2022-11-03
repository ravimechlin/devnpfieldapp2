@staticmethod
def get_rep_id_by_phone(rep_phone):
    ret_list = []
    rep_details = FieldApplicationUser.query(
        ndb.AND
        (
            FieldApplicationUser.rep_phone == rep_phone,
            FieldApplicationUser.current_status > -1
        )
    )

    for rep_detail in rep_details:
        ret_list.append(rep_detail.rep_id)

    return ret_list
