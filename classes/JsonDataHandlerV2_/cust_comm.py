def cust_comm(self):
    self.response.content_type = "application/json"
    ret_json = {"communications": [], "customer": "Nobody"}
    customer = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("identifier"))
    if not customer is None:
        ret_json["customer"] = customer.customer_first_name.strip().title() + " " + customer.customer_last_name.strip().title()
        comms = CustomerComm.query(CustomerComm.field_app_identifier == self.request.get("identifier"))
        objs = []
        rep_ids_to_query = ["-1"]
        for comm in comms:
            obj = {}
            obj["media_url"] = comm.media_url
            if obj["media_url"] == "-1":
                obj["media_url"] = None
            obj["dt"] = comm.dt
            obj["rep_identifier"] = comm.rep_identifier
            if not comm.rep_identifier in rep_ids_to_query:
                rep_ids_to_query.append(comm.rep_identifier)
            obj["rep"] = "Unknown"
            obj["sender_identifier"] = comm.sender
            obj["msg"] = comm.msg
            objs.append(obj)

        rep_identifier_name_dict = {}
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
        for rep in reps:
            rep_identifier_name_dict[rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

        for obj in objs:
            if obj["sender_identifier"] in rep_identifier_name_dict.keys():
                obj["sender"] = rep_identifier_name_dict[obj["sender_identifier"]]
            else:
                obj["sender"] = ret_json["customer"]

        objs = Helpers.bubble_sort(objs, "dt")
        for obj in objs:
            obj["dt"] = str(obj["dt"])
        objs.reverse()
        ret_json["communications"] = objs

    self.response.out.write(json.dumps(ret_json))

