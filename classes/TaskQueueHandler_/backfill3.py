def backfill3(self):
    from datetime import datetime
    import json

    year = int(self.request.get("year"))
    if year == 2016:
        stats = LeaderBoardStat.query(ndb.AND(
            LeaderBoardStat.metric_key == "panels_sold",
            LeaderBoardStat.dt >= datetime(2016, 1, 1),
            LeaderBoardStat.dt <= datetime(2016, 12, 31, 23, 59, 59)
        ))
        keys_to_delete = []
        for stat in stats:
            if stat.metric_key == "panels_sold":
                keys_to_delete.append(stat.key)

        ndb.delete_multi(keys_to_delete)
    

    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)

    stats = LeaderBoardStat.query(ndb.AND(
        LeaderBoardStat.metric_key == "packets_submitted",
        LeaderBoardStat.dt >= start,
        LeaderBoardStat.dt <= end
    ))

    app_ids_to_query = []
    app_identifier_dt_dict = {}
    app_identifier_office_identifier_dict = {}
    app_identifier_rep_id_dict = {}
    for stat in stats:
        app_ids_to_query.append(stat.field_app_identifier)
        app_identifier_dt_dict[stat.field_app_identifier] = stat.dt
        app_identifier_office_identifier_dict[stat.field_app_identifier] = stat.office_identifier
        app_identifier_rep_id_dict[stat.field_app_identifier] = stat.rep_id
    
    app_identifier_panel_qty_dict = {}
    proposals = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(app_ids_to_query))
    for proposal in proposals:
        stats_to_put = []
        deserialized = json.loads(proposal.info)
        if "panel_qty" in deserialized.keys():
            panel_qty = int(deserialized["panel_qty"])
            if "panel_qty_override" in deserialized.keys():
                if deserialized["panel_qty_override"] == True:
                    panel_qty = int(deserialized["new_panel_qty"])

            cnt = 0
            while cnt < panel_qty:
                new_stat = LeaderBoardStat(
                    dt=app_identifier_dt_dict[proposal.field_app_identifier],
                    field_app_identifier=proposal.field_app_identifier,
                    identifier=Helpers.guid(),
                    in_bounds=True,
                    metric_key="panels_sold",
                    office_identifier=app_identifier_office_identifier_dict[proposal.field_app_identifier],
                    pin_identifier="-1",
                    rep_id=app_identifier_rep_id_dict[proposal.field_app_identifier]
                )
                stats_to_put.append(new_stat)
                cnt = cnt + 1

            ndb.put_multi(stats_to_put)

    


