def create_ab_with_call_lb(self):
    h_p_n = Helpers.pacific_now()
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("identifier"))
    if not app_entry is None:
        solar_pro = FieldApplicationUser.first(FieldApplicationUser.identifier == app_entry.lead_generator)
        if not solar_pro is None:
            stat = LeaderBoardStat(
                identifier=Helpers.guid(),
                rep_id=solar_pro.rep_id,                    
                office_identifier=solar_pro.main_office,
                field_app_identifier=app_entry.identifier,
                in_bounds=True,
                pin_identifier="-1",
                metric_key="ab_with_call",
                dt=datetime(h_p_n.year, h_p_n.month, h_p_n.day, 12, 0, 0)
            )
            stat.put()
