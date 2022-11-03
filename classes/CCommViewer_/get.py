def get(self, year, month, day):
    from datetime import datetime
    d = datetime(int(year), int(month), int(day))
    d_end = datetime(d.year, d.month, d.day, 23, 59, 59)
    if d >= datetime(2018, 6, 9):


        rep_ids_to_query = ["-1"]
        app_ids_to_query = ["-1"]
        data = []
        comms = CustomerComm.query(
            ndb.AND(
                CustomerComm.dt >= d,
                CustomerComm.dt <= d_end
            )
        )
        for comm in comms:
            if not comm.rep_identifier in rep_ids_to_query:
                rep_ids_to_query.append(comm.rep_identifier)
            if not comm.field_app_identifier in app_ids_to_query:
                app_ids_to_query.append(comm.field_app_identifier)
            obj = {}
            obj["sender"] = comm.sender
            obj["rep_identifier"] = comm.rep_identifier 
            obj["field_app_identifier"] = comm.field_app_identifier
            obj["rep"] = ""
            obj["customer"] = ""

            obj["msg"] = comm.msg
            obj["dt"] = unicode(str(comm.dt))

            data.append(obj)

        rep_identifier_name_dict = {}
        field_app_identifier_name_dict = {}
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
        for rep in reps:
            rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

        app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(app_ids_to_query))
        for app_entry in app_entries:
            field_app_identifier_name_dict[app_entry.identifier] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()

        for item in data:
            item["rep"] = rep_identifier_name_dict[item["rep_identifier"]]
            item["customer"] = field_app_identifier_name_dict[item["field_app_identifier"]]

        data = Helpers.bubble_sort(data, "dt")
        output = unicode("")
        for item in data:
            logging.info(item)
            sender = None
            recipient = None
            if item["sender"] == item["field_app_identifier"]:
                sender = item["customer"]
                recipient =  item["rep"]
            else:
                sender = item["rep"]
                recipient = item["customer"]

            output += "=========================" + "\r\n"
            output += sender + " => " + recipient + " @ " + item["dt"] + " :" + "\r\n"
            output += "-------------------------" + "\r\n"
            output += item["msg"] + "\r\n"
            output += "=========================" + "\r\n\r\n"

        self.response.content_type = "text/plain"
        self.response.out.write(output)
    else:
        self.response.out.write("data not available.")



        
