def get(self):
    self.response.content_type = "application/json"
    ret_json = {}
    oset = 0
    if (not str(self.request.get("offset")).lower() == "") and (not str(self.request.get("offset")).lower() == "none"):
        oset = int(self.request.get("offset"))

    stats_to_put = []
    if self.request.get("metric") == "leads_acquired":
        app_entries = FieldApplicationEntry.query().order(FieldApplicationEntry.insert_time).fetch(50, offset=oset)
        done = True

        for app_entry in app_entries:
            done = False

            stat_item = LeaderBoardStat(
                identifier=Helpers.guid(),
                rep_id=app_entry.rep_id,
                dt=Helpers.epoch_millis_to_pacific_dt(app_entry.insert_time),
                metric_key="leads_acquired",
                office_identifier=app_entry.office_identifier,
                field_app_identifier=app_entry.identifier,
                in_bounds=True,
                pin_identifier="-1"
            )
            stats_to_put.append(stat_item)

        if len(stats_to_put) > 0:
            if len(stats_to_put) == 1:
                stats_to_put[0].put()
            else:
                ndb.put_multi(stats_to_put)

        ret_json["done"] = done
        if not done:
            ret_json["redirect"] = "https://" + app_identity.get_application_id() + ".appspot.com/seed_leaderboard?metric=leads_acquired&offset=" + str(oset + 50)

    elif self.request.get("metric") == "packets_submitted":
        app_entries = FieldApplicationEntry.query().order(FieldApplicationEntry.insert_time).fetch(50, offset=oset)
        done = True

        app_identifier_tz_dict = {}
        app_identifier_rep_id_dict = {}
        app_ids_to_query = ["-1"]
        app_identifier_office_identifier_dict = {}
        for app_entry in app_entries:

            app_ids_to_query.append(app_entry.identifier)
            app_identifier_rep_id_dict[app_entry.identifier] = app_entry.rep_id
            app_identifier_office_identifier_dict[app_entry.identifier] = app_entry.office_identifier
            done = False

        pp_subs = PerfectPacketSubmission.query(PerfectPacketSubmission.field_application_identifier.IN(app_ids_to_query))
        for pp_sub in pp_subs:
            stat_item = LeaderBoardStat(
                identifier=Helpers.guid(),
                rep_id=app_identifier_rep_id_dict[pp_sub.field_application_identifier],
                dt=pp_sub.rep_submission_date,
                metric_key="packets_submitted",
                office_identifier=app_identifier_office_identifier_dict[pp_sub.field_application_identifier],
                field_app_identifier=pp_sub.field_application_identifier,
                in_bounds=True,
                pin_identifier="-1"
            )
            stats_to_put.append(stat_item)

        if len(stats_to_put) > 0:
            if len(stats_to_put) == 1:
                stats_to_put[0].put()
            else:
                ndb.put_multi(stats_to_put)

        ret_json["done"] = done
        if not done:
            ret_json["redirect"] = "https://" + app_identity.get_application_id() + ".appspot.com/seed_leaderboard?metric=packets_submitted&offset=" + str(oset + 50)

    elif self.request.get("metric") == "appointment_cancelled":
        done = True
        app_entries = FieldApplicationEntry.query().order(FieldApplicationEntry.insert_time).fetch(50, offset=oset)
        app_identifier_rep_id_dict = {}
        app_ids_to_query = ["-1"]
        app_identifier_office_identifier_dict = {}
        for app_entry in app_entries:
            app_ids_to_query.append(app_entry.identifier)
            app_identifier_rep_id_dict[app_entry.identifier] = app_entry.rep_id
            app_identifier_office_identifier_dict[app_entry.identifier] = app_entry.office_identifier
            done = False

        notes = CustomerNote.query(
            ndb.AND
            (
                CustomerNote.note_key == "booking_cancelled",
                CustomerNote.field_app_identifier.IN(app_ids_to_query)
            )
        )
        for note in notes:
            existing_stat = LeaderBoardStat.first(
                ndb.AND
                (
                    LeaderBoardStat.metric_key == "appointment_cancelled",
                    LeaderBoardStat.field_app_identifier == note.field_app_identifier
                )
            )
            if existing_stat is None:
                app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == note.field_app_identifier)
                if not app_entry is None:
                    rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
                    if not rep is None:
                        new_stat = LeaderBoardStat(
                            identifier=Helpers.guid(),
                            rep_id=rep.rep_id,
                            dt=note.inserted_pacific,
                            metric_key="appointment_cancelled",
                            office_identifier=app_entry.office_identifier,
                            field_app_identifier=note.field_app_identifier,
                            in_bounds=True,
                            pin_identifier="-1"
                        )
                        stats_to_put.append(new_stat)

        if len(stats_to_put) > 0:
            if len(stats_to_put) == 1:
                stats_to_put[0].put()
            else:
                ndb.put_multi(stats_to_put)

        ret_json["done"] = done
        if not done:
            ret_json["redirect"] = "https://" + app_identity.get_application_id() + ".appspot.com/seed_leaderboard?metric=appointment_cancelled&offset=" + str(oset + 50)
        

    self.response.out.write(json.dumps(ret_json))

