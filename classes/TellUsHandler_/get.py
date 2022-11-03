def get(self, identifier):
    h_p_t = Helpers.pacific_today()
    start_dt = datetime(h_p_t.year, h_p_t.month, h_p_t.day)
    while not start_dt.isoweekday() == 7:
        start_dt = start_dt + timedelta(days=-1)

    start_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = datetime(start_dt.year, start_dt.month, start_dt.day)
    end_dt = end_dt + timedelta(seconds=-1) + timedelta(days=7)

    start_dt = start_dt + timedelta(days=-7)
    end_dt = end_dt + timedelta(days=-7)


    filename = "tell_us"
    template_data = {}
    template_data["leaderboard_data"] = "{}"
    template_data["identifier"] = identifier
    template_data["week_dt"] = str((start_dt + timedelta(days=7)).date())
    user = FieldApplicationUser.first(FieldApplicationUser.identifier == identifier)
    if not user is None:
        template_data["user_type"] = user.user_type
        template_data["office_identifier"] = user.main_office
        template_data["office_name"] = "n/a"
        office = OfficeLocation.first(OfficeLocation.identifier == user.main_office)
        if not office is None:
            template_data["office_name"] = office.name
        if user.user_type in ["energy_expert", "sales_manager"]:
            
            metric_keys = ["hours_knocked_v2", "leads_acquired", "appointments_kept", "packets_submitted"]
            lb_data = {}
            for key in metric_keys:
                lb_data[key] = 0

            lb_stats = LeaderBoardStat.query(
                ndb.AND(
                    LeaderBoardStat.metric_key.IN(metric_keys),
                    LeaderBoardStat.dt >= start_dt,
                    LeaderBoardStat.dt <= end_dt
                )
            )

            for stat in lb_stats:
                if stat.rep_id == user.rep_id:
                    lb_data[stat.metric_key] += 1

            template_data["leaderboard_data"] = json.dumps(lb_data)

        elif user.user_type == "solar_pro_manager":
            filename = "tell_us_spm"
            template_data["week_dt"] = str((start_dt + timedelta(days=7)).date())

        path = Helpers.get_html_path(filename + ".html")
        self.response.out.write(template.render(path, template_data))

