@staticmethod
def get_admin_sp2_items(email_rep_id, password, start_time=None, end_time=None, office_identifier=None, rep_identifier=None):
    ret_dict = {}
    ret_dict["all_appointments"] = []
    ret_dict["offices"] = []
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
            offices = None
            if office_identifier is None:
                offices = OfficeLocation.query(OfficeLocation.parent_identifier != "n/a")
            else:
                offices = OfficeLocation.query(OfficeLocation.identifier == office_identifier)
            office_id_idx_dict = {}

            for office in offices:
                office_item = {}
                office_item["identifier"] = office.identifier
                office_item["name"] = office.name
                office_item["appointments"] = []
                office_id_idx_dict[office.identifier] = len(ret_dict["offices"])

                ret_dict["offices"].append(office_item)

            if start_time is None:
                start_time = Helpers.pacific_now()

            if end_time is None:
                end_time = start_time + timedelta(days=7)

            app_entries = None
            if office_identifier is None:
                app_entries = FieldApplicationEntry.query(
                    ndb.AND
                    (
                            FieldApplicationEntry.sp_two_time >= start_time,
                            FieldApplicationEntry.sp_two_time <= end_time
                    )
                ).order(FieldApplicationEntry.sp_two_time)
            else:
                app_entries = FieldApplicationEntry.query(
                    ndb.AND
                    (
                            FieldApplicationEntry.sp_two_time >= start_time,
                            FieldApplicationEntry.sp_two_time <= end_time,
                            FieldApplicationEntry.office_identifier == office_identifier
                    )
                ).order(FieldApplicationEntry.sp_two_time)

            rep_email_lst = ["-1"]
            booking_ids_to_query = ["-1"]

            for app_entry in app_entries:
                if app_entry.archived:
                    continue

                o_id = app_entry.office_identifier
                appointment_item = {}
                appointment_item["name"] = app_entry.customer_first_name + " " + app_entry.customer_last_name
                appointment_item["rep_email"] = app_entry.rep_email
                appointment_item["rep_name"] = ""
                appointment_item["ampm"] = "AM"
                rep_email_lst.append(app_entry.rep_email)

                h = app_entry.sp_two_time.hour
                if h > 12:
                    h -= 12
                    appointment_item["ampm"] = "PM"

                appointment_item["hour"] = h;
                appointment_item["minute"] = app_entry.sp_two_time.minute
                appointment_item["month"] = app_entry.sp_two_time.month
                appointment_item["year"] = app_entry.sp_two_time.year
                appointment_item["day"] = app_entry.sp_two_time.day
                appointment_item["address"] = app_entry.customer_address;
                appointment_item["city"] = app_entry.customer_city
                appointment_item["state"] = app_entry.customer_state
                appointment_item["postal"] = app_entry.customer_postal
                appointment_item["booking_identifier"] = app_entry.booking_identifier
                appointment_item["kwh_price"] = app_entry.customer_kwh_price
                appointment_item["actual_kwh_price"] = ""
                appointment_item["system_size"] = ""
                appointment_item["price_per_watt"] = ""
                appointment_item["notes"] = ""

                cpy = json.loads(json.dumps(appointment_item))

                ret_dict["all_appointments"].append(cpy)

                booking_ids_to_query.append(app_entry.booking_identifier)

                ret_dict["offices"][office_id_idx_dict[o_id]]["appointments"].append(appointment_item)

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
                    SheetDataItem.sheet_key == "sp2_master_calendar",
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





            #get the rep name
            users = FieldApplicationUser.query(FieldApplicationUser.rep_email.IN(rep_email_lst))
            for user in users:
                for office_item in ret_dict["offices"]:
                    for appointment_item in office_item["appointments"]:
                        if appointment_item["rep_email"] == user.rep_email:
                            appointment_item["rep_name"] = user.first_name + " " + user.last_name

                for appointment_item in ret_dict["all_appointments"]:
                    if appointment_item["rep_email"] == user.rep_email:
                        appointment_item["rep_name"] = user.first_name + " " + user.last_name


            #delete if there's no associated booking
            booking_ids_to_keep = []
            booking_identifier_fund_dict = {}
            booking_identifier_completion_state_dict = {}
            funds = Helpers.list_funds()
            bookings = SurveyBooking.query(SurveyBooking.identifier.IN(booking_ids_to_query))
            for booking in bookings:
                booking_ids_to_keep.append(booking.identifier)
                booking_identifier_completion_state_dict[booking.identifier] = str(booking.completion_state)
                for fund_item in funds:
                    if fund_item["value"] == booking.fund:
                        booking_identifier_fund_dict[booking.identifier] = fund_item["value_friendly"]

            new_offices = []
            office_cnt = 0
            while office_cnt < len(ret_dict["offices"]):
                office_item = ret_dict["offices"][office_cnt]
                new_office = {}
                new_office["identifier"] = office_item["identifier"]
                new_office["name"] = office_item["name"]
                new_office["appointments"] = []

                for appointment in office_item["appointments"]:
                    try:
                        idx = booking_ids_to_keep.index(appointment["booking_identifier"])
                        appointment["fund"] = booking_identifier_fund_dict[appointment["booking_identifier"]]

                    except:
                        new_offices = new_offices

                    if appointment["booking_identifier"] in booking_identifier_system_size_dict.keys():
                        appointment["system_size"] = booking_identifier_system_size_dict[appointment["booking_identifier"]]

                    if appointment["booking_identifier"] in booking_identifier_actual_kwh_price_dict.keys():
                        appointment["actual_kwh_price"] = booking_identifier_actual_kwh_price_dict[appointment["booking_identifier"]]

                    if appointment["booking_identifier"] in booking_identifier_price_per_watt_dict.keys():
                        appointment["price_per_watt"] = booking_identifier_price_per_watt_dict[appointment["booking_identifier"]]

                    if appointment["booking_identifier"] in booking_identifier_notes_dict.keys():
                        appointment["notes"] = booking_identifier_notes_dict[appointment["booking_identifier"]]

                    if appointment["booking_identifier"] in booking_identifier_completion_state_dict.keys():
                        if not booking_identifier_completion_state_dict[appointment["booking_identifier"]] == "3":
                            new_office["appointments"].append(appointment)

                new_offices.append(new_office);
                office_cnt += 1

            ret_dict["offices"] = new_offices

            new_all_appointments = []
            for appointment in ret_dict["all_appointments"]:
                try:
                    idx = booking_ids_to_keep.index(appointment["booking_identifier"])
                    appointment["fund"] = booking_identifier_fund_dict[appointment["booking_identifier"]]

                except:
                    new_all_appointments = new_all_appointments

                if appointment["booking_identifier"] in booking_identifier_system_size_dict.keys():
                    appointment["system_size"] = booking_identifier_system_size_dict[appointment["booking_identifier"]]

                if appointment["booking_identifier"] in booking_identifier_actual_kwh_price_dict.keys():
                    appointment["actual_kwh_price"] = booking_identifier_actual_kwh_price_dict[appointment["booking_identifier"]]

                if appointment["booking_identifier"] in booking_identifier_price_per_watt_dict.keys():
                    appointment["price_per_watt"] = booking_identifier_price_per_watt_dict[appointment["booking_identifier"]]

                if appointment["booking_identifier"] in booking_identifier_notes_dict.keys():
                    appointment["notes"] = booking_identifier_notes_dict[appointment["booking_identifier"]]

                if appointment["booking_identifier"] in booking_identifier_completion_state_dict.keys():
                    if not booking_identifier_completion_state_dict[appointment["booking_identifier"]] == "3":
                        new_all_appointments.append(appointment)

            ret_dict["all_appointments"] = new_all_appointments

    ret_dict["et"] = str(end_time)
    return ret_dict
