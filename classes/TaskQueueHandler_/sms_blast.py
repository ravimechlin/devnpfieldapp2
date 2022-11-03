def sms_blast(self):
    users = FieldApplicationUser.query(FieldApplicationUser.current_status == 0)
    message = self.request.get("message")
    if self.request.get("option") == "custom":
        users = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(json.loads(self.request.get("custom_recipients"))))        
        for user in users:
            msg = message.replace("{{name}}", user.first_name.strip().title())
            try:
                Helpers.send_sms(user.rep_phone, msg)
            except:
                msg = msg
    else:
        for user in users:
            msg = message.replace("{{name}}", user.first_name.strip().title())
            if self.request.get("option") == "everyone" or ((self.request.get("option") == "reps") and (user.user_type != "super")):
                try:
                    Helpers.send_sms(user.rep_phone, msg)
                except:
                    msg = msg

