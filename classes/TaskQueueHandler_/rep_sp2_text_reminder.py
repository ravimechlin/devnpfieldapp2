def rep_sp2_text_reminder(self):
    from datetime import datetime
    now = Helpers.pacific_now()
    start_dt = datetime(now.year, now.month, now.day)
    end_dt = datetime(now.year, now.month, now.day, 23, 59, 59)
    reps = FieldApplicationUser.query(FieldApplicationUser.current_status == 0)
    for rep in reps:
        if rep.user_type in ["field", "asst_mgr", "co_mgr", "sales_dist_mgr", "rg_mgr", "super", "sales_manager", "energy_expert"]:
            text_msg = ""
            app_entries = FieldApplicationEntry.query(
                ndb.AND(
                    FieldApplicationEntry.sp_two_time >= start_dt,
                    FieldApplicationEntry.sp_two_time <= end_dt
                )
            )

            for app_entry in app_entries:
                if (not app_entry.archived) and (not app_entry.save_me):
                    if app_entry.rep_id == rep.rep_id:
                        am_pm = "AM"
                        hour = app_entry.sp_two_time.hour
                        if hour >= 12:
                            am_pm = "PM"
                        if hour > 12:
                            hour -= 12
                            
                        sp_two_hour_str = str(hour)
                        sp_two_min_str = str(app_entry.sp_two_time.minute)

                        if len(sp_two_hour_str) == 1:
                            sp_two_hour_str = "0" + sp_two_hour_str
                        if len(sp_two_min_str) == 1:
                            sp_two_min_str = "0"  + sp_two_min_str

                        text_msg += (app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + " => " + sp_two_hour_str + ":" + sp_two_min_str + "\n")

            if not text_msg == "":
                try:
                    Helpers.send_sms(rep.rep_phone, text_msg)
                except:
                    text_msg = text_msg
