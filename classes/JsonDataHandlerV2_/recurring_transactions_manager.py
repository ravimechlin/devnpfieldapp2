def recurring_transactions_manager(self):
    f = GCSLockedFile("/ApplicationSettings/recurring_transactions.json")
    content = json.loads(f.read())
    f.lock()
    if self.request.get("type") == "get":
        self.response.content_type = "application/json"
        ret_json = {"transactions": [], "reps": {}}
        rep_ids_to_query = ["-1"]
        
        ret_json["transactions"] = content
        for item in ret_json["transactions"]:
            for rep_identifier in item["recipients"]:
                if not rep_identifier in rep_ids_to_query:
                    rep_ids_to_query.append(rep_identifier)
        f.unlock()
        reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_ids_to_query))
        for rep in reps:
            ret_json["reps"][rep.identifier] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()

        self.response.out.write(json.dumps(ret_json))
    elif self.request.get("type") == "create_transaction":
        self.response.content_type = "application/json"
        ret_json = {"identifier": Helpers.guid()}
        item = {"recipients": [], "payload": json.loads(self.request.get("payload")), "active": True, "identifier": ret_json["identifier"], "frequency": self.request.get("frequency"), "do_not_generate_payout": self.request.get("do_not_generate_payout")}
        content.append(item)
        f.unlock()
        f.write(json.dumps(content), "application/json", "public-read")
        self.response.out.write(json.dumps(ret_json))

    elif self.request.get("type") == "add_user":
        self.response.content_type = "application/json"
        ret_json = {"success": False}
        for item in content:
            if item["identifier"] == self.request.get("identifier"):
                found = False
                for recipient in item["recipients"]:
                    if recipient == self.request.get("recipient"):
                        found = True
                if not found:
                    ret_json["success"] = True
                    user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("recipient"))
                    if not user is None:
                        ret_json["name"] = user.first_name + " " + user.last_name
                        item["recipients"].append(self.request.get("recipient"))
                        f.unlock()
                        f.write(json.dumps(content), "application/json", "public-read")                        
        f.unlock()
        self.response.out.write(json.dumps(ret_json))

    elif self.request.get("type") == "drop_transaction":
        new_transactions = []
        for item in content:
            if not (item["identifier"] == self.request.get("identifier")):
                new_transactions.append(item)
        f.unlock()
        f.write(json.dumps(new_transactions), "application/json", "public-read")

    elif self.request.get("type") == "rename_description":
        for item in content:
            if item["identifier"] == self.request.get("identifier"):
                item["payload"]["description"] = self.request.get("description")
        f.unlock()
        f.write(json.dumps(content), "application/json", "public-read")

    elif self.request.get("type") == "activate_deactivate":
        for item in content:
            if item["identifier"] == self.request.get("identifier"):
                item["active"] = (self.request.get("status") == "1")
        f.unlock()
        f.write(json.dumps(content), "application/json", "public-read")

    elif self.request.get("type") == "drop_user":
        for item in content:
            if item["identifier"] == self.request.get("identifier"):
                new_recipients = []
                for person in item["recipients"]:
                    if not (person == self.request.get("person")):
                        new_recipients.append(person)
                item["recipients"] = new_recipients

                f.unlock()
                f.write(json.dumps(content), "application/json", "public-read")
