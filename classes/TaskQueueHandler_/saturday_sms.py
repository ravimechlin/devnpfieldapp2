def saturday_sms(self):
    msg = "HAPPY SATURDAY EVENING!  Please go to the field app NOW and update your numbers and goals."
    reps = FieldApplicationUser.query(
        ndb.AND
        (
            FieldApplicationUser.current_status == 0,
        )
    )
    for rep in reps:
        if not rep.user_type == "super":
            try:
                Helpers.send_sms(rep.rep_phone, msg)
            except:
                msg = msg

