def post(self):
    import json
    from google.appengine.api import app_identity
    
    fromm = str(self.request.get("From")).split("+")[1]
    if len(fromm) == 11:
        fromm = fromm[1:]

    to = str(self.request.get("To"))
    if len(to) == 11:
        to = to[1:]
    elif len(to) == 12:
        to = to[2:]

    mapping = {"6194898681": "9514046912", "6194898676": "4358687415", "6194899203": "8017030001", "9513385574": "8584147413", "9513374684": "9517290802", "9513385565": "6614925737", "8312735984": "8312750754"}
    
    if to in ["6194898681", "6194898676", "6194899203", "9513385574", "9513374684", "9513385565", "8312735984"]:
        rep = FieldApplicationUser.first(FieldApplicationUser.rep_phone == mapping[to])
        if not rep is None:
            self.response.content_type = "application/xml"
            Helpers.send_sms(mapping[to], "New Message From Postal Mailer Campaign: \"" + unicode(self.request.get("Body")) + "\". DON'T REPLY TO THIS TEXT, instead reply here: https://" + app_identity.get_application_id() + ".appspot.com/PostalCampaignThread/" + fromm + "/" + rep.identifier)

            content = []
            if Helpers.gcs_file_exists("/PostalCampaign/texts.json"):
                f = GCSLockedFile("/PostalCampaign/texts.json")
                content = json.loads(f.read())
                f.unlock() 
            
            content.append({"to": to, "from": fromm, "type": "sms", "dt": str(Helpers.pacific_now()).split(".")[0]})
            f2 = GCSLockedFile("/PostalCampaign/texts.json")
            f2.write(json.dumps(content), "application/json", "public-read")
            f2.unlock()

            item = PostalCampaignMessageV2(
                identifier=Helpers.guid(),
                rep_identifier="-1",
                customer_phone=fromm,
                dt=Helpers.pacific_now(),
                content=unicode(self.request.get("Body"))
            )
            item.put()
        return



    body = unicode(self.request.get("Body"))
        
    img = str(self.request.get("MediaUrl0"))
    if not fromm == "":
        sender = "Unknown Person"
        usr = FieldApplicationUser.first(FieldApplicationUser.rep_phone == fromm)
        if not usr is None:
            sender = usr.first_name.strip().title() + " " + usr.last_name.strip().title()

        msg_body = body
        if len(img) > 4:
            msg_body += "...attachment: " + img

        act_name = "Twilio Message Received"
        subject = "Twilio Message From " + sender
        if to == "9518015044":
            subject = "Twilio Message (Calendar Event Reply) From " + sender
            act_name = "Twilio Calendar Event SMS Reply"
        notification = Notification.first(Notification.action_name == act_name)
        if not notification is None:
            for person in notification.notification_list:
                Helpers.send_email(person.email_address, subject, msg_body)



    logging.info(self.request.POST)
    logging.info(self.request.POST.__dict__)
    logging.info(self.request.get("Body"))
    logging.info(self.request.get("From").split("+")[1])
    logging.info(self.request.get("MediaUrl0"))
    logging.info(str(self.request.get("To")))
    return
    body = self.request.get("Body")
    sender = self.request.get("From").split("+")[1]
    sender = sender[1:]
    msg = "sry but couldn't compute, kk my bad.."
    if not sender == "8312750754":
        if not sender == "8179953266":
            msg = "sry only ray and thomas allowed for now...."
            Helpers.send_sms(sender, msg)
            return

    found_results = False
    processed_query = False
    if "<=" in body:
        vals = body.split("<=")
        stripped_vals = []
        for v in vals:
            stripped_vals.append(v.strip())

        if stripped_vals[0] == "dob":
            processed_query = True
            index = search.Index(name="cust_names")
            results = index.search(stripped_vals[1])

            field_app_identifier_idx_dict = {}
            field_app_ids_to_query = ["-1"]

            for result in results:
                result_item = {}
                for field in result.fields:
                    if field.name == "cust_identifier":
                        result_item["identifier"] = field.value
                field_app_ids_to_query.append(result_item["identifier"])

            msg = "Sorry no results"
            app_entries = FieldApplicationEntry.query(FieldApplicationEntry.identifier.IN(field_app_ids_to_query))
            for a in app_entries:
                found_results = True
                inner_msg = "Result: " + a.customer_first_name.strip().title() +  " " + a.customer_last_name.strip().title() + ". Info: " + str(a.customer_dob)
                Helpers.send_sms(sender, inner_msg)

            if not found_results:
                Helpers.send_sms(sender, msg)

    if not processed_query:
        Helpers.send_sms(sender, msg)



    logging.info(self.request.get("From"))
    logging.info(self.request.get("Body").lower())
