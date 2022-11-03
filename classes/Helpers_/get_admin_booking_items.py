@staticmethod
def get_admin_booking_items(email_rep_id, password, start_time=None, end_time=None, office_identifier=None, rep_identifier=None):
    ret_dict = {}
    ret_dict["states"] = []

    ca_dict = {"name": "CA", "appointments": []}
    ut_dict = {"name": "UT", "appointments": []}

    state_idx_list = ["CA", "UT"]

    ret_dict["states"].append(ca_dict)
    ret_dict["states"].append(ut_dict)
    ret_dict["success"] = False

    pw = Helpers.hash_pass(password)
    users = FieldApplicationUser.query(
        ndb.OR
        (
            ndb.AND
            (
                FieldApplicationUser.rep_email == email_rep_id,
                FieldApplicationUser.password == pw
            ),
            ndb.AND
            (
                FieldApplicationUser.rep_id == email_rep_id,
                FieldApplicationUser.password == pw
            )
        )
    )

    for user in users:
        if user.user_type == "super":
            ret_dict["success"] = True

            if start_time is None:
                start_time =  int(time.time() * 1000)
                start_time -= (1000 * 60 * 60 * 24 * 10)

            if end_time is None:
                end_time = int(time.time() * 1000)

            app_entries = FieldApplicationEntry.query(
                ndb.AND
                (
                    FieldApplicationEntry.insert_time >= start_time,
                    FieldApplicationEntry.insert_time <= end_time
                )
            )
            app_entry_list = []
            booking_ids_to_query = ["-1"]
            app_identifier_idx_dict = {}
            rep_ids_to_query = ["-1"]
            cnt = 0
            for app_entry in app_entries:
                if not app_entry.archived:
                    app_identifier_idx_dict[app_entry.identifier] = cnt
                    app_entry_list.append(app_entry)
                    booking_ids_to_query.append(app_entry.booking_identifier)
                    rep_ids_to_query.append(app_entry.rep_id)
                    cnt += 1

            booking_list = []
            booking_ids_found = []
            booking_identifier_booking_date_dict = {}

            bookings = SurveyBooking.query(SurveyBooking.identifier.IN(booking_ids_to_query))
            for booking in bookings:
                if (not (int(booking.completion_state) == 3)) and (not booking.booking_year == 1970):
                    booking_identifier_booking_date_dict[booking.identifier] = date(booking.booking_year, booking.booking_month, booking.booking_day)
                    booking_ids_found.append(booking.identifier)
                    booking_list.append(booking)

            #try to query for the system size
            booking_identifier_system_size_dict = {}
            booking_identifier_actual_kwh_price_dict = {}
            booking_identifier_price_per_watt_dict = {}
            booking_identifier_notes_dict = {}

            pp_approvals = PerfectPacketApproval.query(PerfectPacketApproval.booking_identifier.IN(booking_ids_to_query))
            for pp_approval in pp_approvals:
                booking_identifier_system_size_dict[pp_approval.booking_identifier] = pp_approval.system_size

            sd_items = SheetDataItem.query(
                ndb.AND(
                    SheetDataItem.entity_identifier.IN(booking_ids_to_query),
                    SheetDataItem.sheet_key == "master_survey_schedule",
                    SheetDataItem.cell_key.IN(["system_size", "actual_kwh_price", "price_per_watt", "notes"])
                )
            )

            for sd_item in sd_items:
                if sd_item.cell_key == "system_size":
                    booking_identifier_system_size_dict[sd_item.entity_identifier] = sd_item.cell_value
                elif sd_item.cell_key == "actual_kwh_price":
                    booking_identifier_actual_kwh_price_dict[sd_item.entity_identifier] = sd_item.cell_value
                elif sd_item.cell_key == "price_per_watt":
                    booking_identifier_price_per_watt_dict[sd_item.entity_identifier] = sd_item.cell_value
                elif sd_item.cell_key == "notes":
                    booking_identifier_notes_dict[sd_item.entity_identifier] = sd_item.cell_value
                else:
                    booking_identifier_system_size_dict = booking_identifier_system_size_dict

            users = FieldApplicationUser.query(FieldApplicationUser.rep_id.IN(rep_ids_to_query))

            rep_id_rep_name_dict = {}
            rep_id_rep_phone_dict = {}
            rep_id_rep_email_dict = {}

            for user in users:
                rep_id_rep_name_dict[user.rep_id] = (user.first_name.strip() + " " + user.last_name.strip()).title()
                rep_id_rep_phone_dict[user.rep_id] = Helpers.format_phone_number(user.rep_phone)
                rep_id_rep_email_dict[user.rep_id] = user.rep_email

            for app_entry_item in app_entry_list:
                if app_entry_item.booking_identifier in booking_ids_found:
                    appointment_item = {}
                    appointment_item["identifier"] = app_entry_item.identifier
                    appointment_item["timestamp"] = app_entry_item.insert_time
                    appointment_item["survey_date"] = booking_identifier_booking_date_dict[app_entry_item.booking_identifier]
                    appointment_item["rep_name"] = rep_id_rep_name_dict[app_entry_item.rep_id]
                    appointment_item["rep_email"] = rep_id_rep_email_dict[app_entry_item.rep_id]
                    appointment_item["rep_phone"] = rep_id_rep_phone_dict[app_entry_item.rep_id]
                    appointment_item["rate"] = app_entry_item.customer_kwh_price
                    appointment_item["address"] = app_entry_item.customer_address
                    appointment_item["city"] = app_entry_item.customer_city
                    appointment_item["state"] = app_entry_item.customer_state
                    appointment_item["postal"] = app_entry_item.customer_postal
                    appointment_item["sp2_time"] = str(app_entry_item.sp_two_time)
                    appointment_item["booking_identifier"] = app_entry_item.booking_identifier
                    appointment_item["system_size"] = ""
                    appointment_item["actual_kwh_price"] = ""
                    appointment_item["price_per_watt"] = ""
                    appointment_item["notes"] = ""

                    if app_entry_item.booking_identifier in booking_identifier_system_size_dict.keys():
                        appointment_item["system_size"] = booking_identifier_system_size_dict[appointment_item["booking_identifier"]]

                    if app_entry_item.booking_identifier in booking_identifier_actual_kwh_price_dict.keys():
                        appointment_item["actual_kwh_price"] = booking_identifier_actual_kwh_price_dict[appointment_item["booking_identifier"]]

                    if app_entry_item.booking_identifier in booking_identifier_price_per_watt_dict.keys():
                        appointment_item["price_per_watt"] = booking_identifier_price_per_watt_dict[appointment_item["booking_identifier"]]

                    if app_entry_item.booking_identifier in booking_identifier_notes_dict.keys():
                        appointment_item["notes"] = booking_identifier_notes_dict[appointment_item["booking_identifier"]]

                    idx = -1
                    try:
                        idx = state_idx_list.index(appointment_item["state"])
                    except:
                        idx = idx

                    if not idx == -1:
                        ret_dict["states"][idx]["appointments"].append(appointment_item)





            appointment_item = {}

            #delete if there's no associated booking
            #booking_ids_to_keep = []
            #booking_identifier_fund_dict = {}
            #booking_identifier_completion_state_dict = {}
            #funds = Helpers.list_funds()
            #bookings = SurveyBooking.query(SurveyBooking.identifier.IN(booking_ids_to_query))
            #for booking in bookings:
            #    booking_ids_to_keep.append(booking.identifier)
            #    booking_identifier_completion_state_dict[booking.identifier] = str(booking.completion_state)
            #    for fund_item in funds:
            #        if fund_item["value"] == booking.fund:
            #            booking_identifier_fund_dict[booking.identifier] = fund_item["value_friendly"]

            #new_offices = []
            #office_cnt = 0
            #while office_cnt < len(ret_dict["offices"]):
            #    office_item = ret_dict["offices"][office_cnt]
            #    new_office = {}
            #    new_office["identifier"] = office_item["identifier"]
            #    new_office["name"] = office_item["name"]
            #    new_office["appointments"] = []

             #   for appointment in office_item["appointments"]:
              #      try:
               #         idx = booking_ids_to_keep.index(appointment["booking_identifier"])
                #        appointment["fund"] = booking_identifier_fund_dict[appointment["booking_identifier"]]

                 #   except:
                  #      new_offices = new_offices

                   # if appointment["booking_identifier"] in booking_identifier_system_size_dict.keys():
                   #     appointment["system_size"] = booking_identifier_system_size_dict[appointment["booking_identifier"]]

             #       if appointment["booking_identifier"] in booking_identifier_actual_kwh_price_dict.keys():
              #          appointment["actual_kwh_price"] = booking_identifier_actual_kwh_price_dict[appointment["booking_identifier"]]

               #     if appointment["booking_identifier"] in booking_identifier_price_per_watt_dict.keys():
                #        appointment["price_per_watt"] = booking_identifier_price_per_watt_dict[appointment["booking_identifier"]]

                 #   if appointment["booking_identifier"] in booking_identifier_notes_dict.keys():
                  #      appointment["notes"] = booking_identifier_notes_dict[appointment["booking_identifier"]]

                   # if appointment["booking_identifier"] in booking_identifier_completion_state_dict.keys():
                    #    if not booking_identifier_completion_state_dict[appointment["booking_identifier"]] == "3":
                     #       new_office["appointments"].append(appointment)

                #new_offices.append(new_office);
                #office_cnt += 1

            #ret_dict["offices"] = new_offices

            #new_all_appointments = []
            #for appointment in ret_dict["all_appointments"]:
            ##    try:
              #      idx = booking_ids_to_keep.index(appointment["booking_identifier"])
              #      appointment["fund"] = booking_identifier_fund_dict[appointment["booking_identifier"]]

#                except:
 #                   new_all_appointments = new_all_appointments

  #              if appointment["booking_identifier"] in booking_identifier_system_size_dict.keys():
   #                 appointment["system_size"] = booking_identifier_system_size_dict[appointment["booking_identifier"]]

    #            if appointment["booking_identifier"] in booking_identifier_actual_kwh_price_dict.keys():
     #               appointment["actual_kwh_price"] = booking_identifier_actual_kwh_price_dict[appointment["booking_identifier"]]

      #          if appointment["booking_identifier"] in booking_identifier_price_per_watt_dict.keys():
       #             appointment["price_per_watt"] = booking_identifier_price_per_watt_dict[appointment["booking_identifier"]]

        #        if appointment["booking_identifier"] in booking_identifier_notes_dict.keys():
         #           appointment["notes"] = booking_identifier_notes_dict[appointment["booking_identifier"]]

          #      if appointment["booking_identifier"] in booking_identifier_completion_state_dict.keys():
           #         if not booking_identifier_completion_state_dict[appointment["booking_identifier"]] == "3":
            #            new_all_appointments.append(appointment)

            #ret_dict["all_appointments"] = new_all_appointments

    for item in ret_dict["states"]:
        item["appointments"] = Helpers.bubble_sort(item["appointments"], "survey_date")
        for appt in item["appointments"]:
            appt["survey_date"] = str(appt["survey_date"])

    ret_dict["et"] = str(end_time)
    return ret_dict
