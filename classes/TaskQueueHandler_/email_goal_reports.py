def email_goal_reports(self):
    import tablib
    import base64
    from datetime import datetime
    from datetime import timedelta
    dt = Helpers.pacific_now()
    while not dt.isoweekday() == 7:
        dt = dt + timedelta(days=-1)
    
    end_dt = dt + timedelta(days=6)
    start_dt = dt

    logging.info(str(dt.date()))
    goals = RepGoal.query(RepGoal.start_date >= dt.date())
    rep_identifiers_to_query = ["-1"]
    rep_identifier_goals_dict = {}    
    for goal in goals:
        rep_identifiers_to_query.append(goal.rep_identifier)
        rep_identifier_goals_dict[goal.rep_identifier] = json.loads(goal.goal_info)


    rep_identifier_office_identifier_dict = {}
    distinct_offices = ["-1"]
    office_identifier_reps_list = {}
    rep_identifier_email_dict = {}
    rep_identifier_phone_dict = {}
    rep_identifier_name_dict = {}
    if len(rep_identifiers_to_query) > 1:
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_identifiers_to_query))
        for rep in reps:
            rep_identifier_office_identifier_dict[rep.identifier] = rep.main_office
            if not rep.main_office in distinct_offices:
                distinct_offices.append(rep.main_office)
            if not rep.main_office in office_identifier_reps_list.keys():
                office_identifier_reps_list[rep.main_office] = []
            office_identifier_reps_list[rep.main_office].append(rep.identifier)
            rep_identifier_email_dict[rep.identifier] = rep.rep_email
            rep_identifier_phone_dict[rep.identifier] = Helpers.format_phone_number(rep.rep_phone)
            rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + rep.last_name.strip().title()

        offices = OfficeLocation.query(OfficeLocation.identifier.IN(distinct_offices))
        for office in offices:
            email_body = "Rep   Phone   Email   ACs Goal   AKs Goal   CDs goal\r\n"
            headers = ('Rep', 'Phone', 'Email', 'ACs Goal', 'AKs Goal', 'CDs goal')
            data = []

            for rep_identifier in office_identifier_reps_list[office.identifier]:
                email_body += rep_identifier_name_dict[rep_identifier]
                email_body += "   "
                email_body += rep_identifier_phone_dict[rep_identifier]
                email_body += "   "
                email_body += rep_identifier_email_dict[rep_identifier]
                email_body += "   "
                email_body += str(rep_identifier_goals_dict[rep_identifier]["AC"])
                email_body += "   "
                email_body += str(rep_identifier_goals_dict[rep_identifier]["AK"])
                email_body += "   "
                email_body += str(rep_identifier_goals_dict[rep_identifier]["CD"])
                email_body += "\r\n"

                data.append((rep_identifier_name_dict[rep_identifier],
                             rep_identifier_phone_dict[rep_identifier],
                             rep_identifier_email_dict[rep_identifier],
                             rep_identifier_goals_dict[rep_identifier]["AC"],
                             rep_identifier_goals_dict[rep_identifier]["AK"],
                             rep_identifier_goals_dict[rep_identifier]["CD"]))

            structured_data = tablib.Dataset(*data, headers=headers)
            attachment_data = {}
            attachment_data["data"] = [base64.b64encode(structured_data.csv)]
            attachment_data["content_types"] = ["text/csv"]
            attachment_data["filenames"] = [office.name.replace(" ", "_") + "_Rep_Goals_" + str(dt.date()) + "_" + str(end_dt.date())]

            distribution_list = json.loads(office.distribution_list)
            for recipient in distribution_list:
                Helpers.send_email(recipient, office.name + " Rep Goals Report (" + str(start_dt.date()) + " - " + str(end_dt.date()) + ")", email_body, attachment_data)
