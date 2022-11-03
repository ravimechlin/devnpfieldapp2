def export_payment_history_for_rep(self):
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib

    start_vals = self.request.get("start").split("-")
    end_vals = self.request.get("end").split("-")
    start = date(int(start_vals[0]), int(start_vals[1]), int(start_vals[2]))
    end = date(int(end_vals[0]), int(end_vals[1]), int(end_vals[2]))
    transactions = MonetaryTransactionV2.query(
        ndb.AND
        (
            MonetaryTransactionV2.recipient == self.request.get("identifier"),
            MonetaryTransactionV2.payout_date >= start,
            MonetaryTransactionV2.payout_date <= end
        )
    )

    reimbursement_dollars = 0
    reimbursement_cents = 0
    other_dollars = 0
    other_cents = 0
    gross_dollars = 0
    gross_cents = 0

    headers = ('Date', 'Amount', 'Is Reimbursement', 'Description', 'Image')
    data = []
    for t in transactions:
        if not t.approved or t.denied:
            continue       
        is_reimbursement = ("reimbursement" in t.description_key.lower())
        is_other = (not is_reimbursement)
        reimbursement_dollars += (t.dollars * is_reimbursement)
        reimbursement_cents += (t.cents * is_reimbursement)
        other_dollars += (t.dollars * is_other)
        other_cents += (t.cents * is_other)
        gross_dollars += (t.dollars)
        gross_cents += (t.cents)

        if reimbursement_cents >= 100:
            reimbursement_dollars += 1
            reimbursement_cents -= 100
        if reimbursement_cents <= -100:
            reimbursement_cents -= 1
            reimbursement_cents += 100
        if other_cents >= 100:
            other_dollars += 1
            other_cents -= 100
        if other_cents <= -100:
            other_dollars -= 1
            other_cents += 100

        if gross_cents >= 100:
            gross_dollars += 1
            gross_cents -= 100
        if gross_cents <= -100:
            gross_dollars -= 1
            gross_cents += 100

        month = str(t.payout_date.month)
        if len(month) == 1:
            month = "0" + month
        day = str(t.payout_date.day)
        if len(day) == 1:
            day = "0" + day
        year = str(t.payout_date.year)
        dt = month + "/" + day + "/" + year

        amt = ""
        if t.cents < 0:
            cents = str(t.cents * -1)
            if len(cents) == 1:
                cents = "0" + cents
            amt = "-" + "$" + str(t.dollars * -1) + "." + cents
        else:
            cents = str(t.cents)
        if len(cents) == 1:
            cents = "0" + cents
        amt = "$" + str(t.dollars) + "." + cents
        bool_lst = ["No", "Yes"]
        image_link = ""
        if is_reimbursement:
            info_dct = json.loads(t.extra_info)
            if "file_extension" in info_dct.keys():
                image_link = "https://storage.googleapis.com/" + app_identity.get_default_gcs_bucket_name() + "/Images/Receipts/" + t.identifier + "." + info_dct["file_extension"]
        data.append((str(t.payout_date.year), amt, bool_lst[int(is_reimbursement)], t.description.encode("ascii", "ignore"), image_link)) 
    
    data.append(("", "", "", "", ""))
    data.append(("", "", "", "", ""))
    data.append(("", "", "", "", ""))
    data.append(("Gross", "Reimbursement", "Other", "", ""))        

    gg = float(gross_dollars) + float(float(gross_cents) * 0.01)
    rr = float(reimbursement_dollars) + float(float(reimbursement_cents) * 0.01)
    oo = float(other_dollars) + float(float(other_cents) * 0.01)

    data.append((Helpers.currency_format(gg), Helpers.currency_format(rr), Helpers.currency_format(oo), "", ""))

    structured_data = tablib.Dataset(*data, headers=headers)
    rep = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not rep is None:
        #attachment_data = {}
        #attachment_data["content_types"] = ["text/csv"]
        #attachment_data["filenames"] = ['_'.join(start_vals) + "__" + '_'.join(end_vals) + rep.last_name.strip().lower() + "_" + rep.first_name.strip().lower() + ".csv"]
        #attachment_data["data"] = [base64.b64encode(structured_data.csv)]
        
        #Helpers.send_email(rep.rep_email,
                            #"Field App Payment Export",
                            #"Attached is your data from " + self.request.get("start") + " - " + self.request.get("end") + "...",
                            #attachment_data
        #)
        file_id = hashlib.md5(Helpers.guid()).hexdigest()
        f = GCSLockedFile("/PaymentHistoryExports/" + file_id + ".csv")
        f.write(structured_data.csv, "text/csv", "public-read")
        time.sleep(10)
        
        attachment_data = {}
        attachment_data["data"] = []
        attachment_data["content_types"] = []
        attachment_data["filenames"] = []

        attachment_data["data"].append(base64.b64encode(structured_data.csv))
        attachment_data["content_types"].append("text/csv")
        attachment_data["filenames"].append(file_id + ".csv")


        Helpers.send_email(rep.rep_email, "Field App Payments Export", "Attached is your export data...", attachment_data)
        time.sleep(30)
        bucket_name = os.environ.get('BUCKET_NAME',
                                app_identity.get_default_gcs_bucket_name())

        bucket = '/' + bucket_name
        filename = bucket + "/PaymentHistoryExports/" + file_id + ".csv"
        gcs.delete(filename)
