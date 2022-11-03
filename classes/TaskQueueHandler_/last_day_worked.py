def last_day_worked(self):
    yesterday = Helpers.pacific_now() + timedelta(days=-1)
    start_dt = datetime(yesterday.year, yesterday.month, yesterday.day)
    end_dt = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

    stats = LeaderBoardStat.query(
        ndb.AND(
            LeaderBoardStat.metric_key == "hours_knocked_v2",
            LeaderBoardStat.dt >= start_dt,
            LeaderBoardStat.dt <= end_dt
        )
    )

    unique_rep_ids = []
    for stat in stats:
        if not stat.rep_id in unique_rep_ids:
            unique_rep_ids.append(stat.rep_id)

    if len(unique_rep_ids) > 0:
        reps = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(unique_rep_ids))

        for rep in reps:
            f = GCSLockedFile("/EmploymentDates/" + rep.identifier + ".txt")
            f.write(str(rep.registration_date) + " --- " + str(yesterday.date()), "text/plain", "public-read")
            f.unlock()


    
