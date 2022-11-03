def rep_payroll_notify(self):
    lst = json.loads(self.request.get("list"))
    msg = Helpers.read_setting("paycheck_ready_message")
    for item in lst:
        try:
            Helpers.send_sms(item, msg)
        except:
            msg = msg

