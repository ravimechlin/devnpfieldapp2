def auto_archive_ptos(self):
    from datetime import datetime, timedelta
    cnt = 0
    pp_subs = PerfectPacketSubmission.query(
        ndb.AND(
            PerfectPacketSubmission.archived == False,
            PerfectPacketSubmission.save_me == False
        )
    )
    for pp_sub in pp_subs:
        info = json.loads(pp_sub.extra_info)
        if "project_management_checkoffs" in info.keys():
            if "received_pto" in info["project_management_checkoffs"].keys():
                if "checked" in info["project_management_checkoffs"]["received_pto"].keys():
                    if info["project_management_checkoffs"]["received_pto"]["checked"]:
                        if "date" in info["project_management_checkoffs"]["received_pto"].keys():
                            d = info["project_management_checkoffs"]["received_pto"]["date"]
                            split = d.split("-")
                            dt = datetime(int(split[0]), int(split[1]), int(split[2]))
                            ninety_days_ago = Helpers.pacific_now() + timedelta(days=-90)
                            if dt < ninety_days_ago:
                                Helpers.archive_state(pp_sub.field_application_identifier)
                                cnt += 1

    #Helpers.send_email("rnirnber@gmail.com", "Auto-Archive PTO count", str(cnt))

