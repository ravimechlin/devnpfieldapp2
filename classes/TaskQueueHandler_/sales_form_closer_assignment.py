def sales_form_closer_assignment(self):
    import time
    from google.appengine.api import app_identity

    closer = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("closer"))
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("app_entry_identifier"))
    if (not closer is None) and not (app_entry is None):
        closer_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "accepts_leads_" + str(Helpers.pacific_today()) + "_" + closer.identifier)
        if not closer_kv is None:
            x = 25
            #closer_kv.key.delete()

        time.sleep(3)
        req_headers = {}
        req_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        req_headers["Accept-Language"] = "en-US,en;q=0.8"
        req_headers["Cache-Control"] = "max-age=0"
        req_headers["Connection"] = "keep-alive"
        req_headers["Host"] = "tools.cleanpowerfinance.com"
        req_headers["Referer"] = "https://www.google.com"
        req_headers["User-Agent"] = "The field app just hacked itself ;) - RJN"

        form_fields1 = {}
        form_fields1["fn"] = "reassign_customer"
        form_fields1["identifier"] = app_entry.identifier
        form_fields1["rep_id"] = closer.rep_id
        form_fields1["skip_text"] = "1"

        resp = urlfetch.fetch(
            url="https://" + app_identity.get_application_id() + ".appspot.com/data",
            method=urlfetch.POST,
            payload=urllib.urlencode(form_fields1),
            deadline=60,
            headers=req_headers,
            follow_redirects=True
        )

        form_fields2 = {}
        form_fields2["fn"] = "process_app_entry"
        form_fields2["identifier"] = app_entry.identifier
        form_fields2["rep_identifier"] = closer.identifier
        form_fields2["skip_text"] = str(int((self.request.get("appointment_type") in ["same_day_right_now", "same_day_later_on"])))

        resp = urlfetch.fetch(
            url="https://" + app_identity.get_application_id() + ".appspot.com/data",
            method=urlfetch.POST,
            payload=urllib.urlencode(form_fields2),
            deadline=60,
            headers=req_headers,
            follow_redirects=True
        )

        assigned_kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy=closer.identifier + "_same_day_assignment_" + str(Helpers.pacific_today()),
            val="1",
            expiration=Helpers.pacific_now() + timedelta(days=3)
        ) 
        assigned_kv.put()

        sp2_str = ""
        if str(self.request.get("appointment_type")) in ["same_day_right_now", "same_day_later_on"]:
            if str(self.request.get("appointment_type")) == "same_day_right_now":
                sp2_str = "SP2 Time: RIGHT NOW"
            else:
                am_pm = "AM"
                hour = app_entry.sp_two_time.hour
                if hour >= 12:
                    am_pm = "PM"
                if hour > 12:
                    hour -= 12
                sp2_str = "SP2 Time: " + str(hour) + ":00 " + am_pm

        if str(self.request.get("appointment_type")) in ["same_day_right_now", "same_day_later_on"]:
            lead_generator = FieldApplicationUser.first(FieldApplicationUser.identifier == app_entry.lead_generator)
            if not lead_generator is None:
                sp_text = "You just assigned a same day to " + closer.first_name.strip().title() + " " + closer.last_name.strip().title() + ". They are going to call you to confirm it and give their ETA. Stay in the house until they arrive! Closer phone: " + Helpers.format_phone_number(closer.rep_phone)
                if str(self.request.get("appointment_type")) == "same_day_right_now":
                    Helpers.send_sms(lead_generator.rep_phone, sp_text)

            rep_text = "SAME DAY!  " + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + " at " + app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal + " SP: " + lead_generator.first_name.strip().title() + " " + lead_generator.last_name.strip().title() + ". SP Phone: " + Helpers.format_phone_number(lead_generator.rep_phone) + " " + sp2_str + ". Please call the SP NOW and confirm/give your ETA!" 
            Helpers.send_sms(closer.rep_phone, rep_text)
