def bulk_payroll_export(self):
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    from google.appengine.api import app_identity
    user = FieldApplicationUser.first(
        ndb.AND
        (
            FieldApplicationUser.rep_email == self.request.get("login"),
            FieldApplicationUser.password == Helpers.hash_pass(self.request.get("password"))
        )
    )
    if not user is None:
        if user.user_type == "super":
            token = self.request.get("token")
            start_date = date(int(self.request.get("year")), 1, 1)
            end_date = date(int(self.request.get("year")), 12, 31)
            
            if self.request.get("custom_range") == "1":
                start_date = date(int(self.request.get("start_year")), int(self.request.get("start_month")), 1)
                end_date = datetime(int(self.request.get("end_year")), int(self.request.get("end_month")), 1)

                month = end_date.month
                month_change = False
                while not month_change:
                    end_date = end_date + timedelta(days=1)
                    month_change = (not end_date.month == month)
                end_date = end_date + timedelta(days=-1)
                end_date = end_date.date()

            transactions = MonetaryTransactionV2.query(
                ndb.AND
                (
                    MonetaryTransactionV2.payout_date >= start_date,
                    MonetaryTransactionV2.payout_date <= end_date,
                )
            )

            data = []
            rep_identifier_name_dict = {}
            rep_identifiers_to_query = ["-1"]

            bool_map = ["No", "Yes"]

            check_user_discriminants = False
            check_keyword_discriminants = False
            user_discriminants = []
            keyword_discriminants = []
            if not (self.request.get("users_discriminant") == "n/a"):
                check_user_discriminants = True
                user_discriminants = self.request.get("users_discriminant").split("|")

            if not(self.request.get("description_keyword_list") == "n/a"):
                check_keyword_discriminants = True
                keyword_vals = self.request.get("description_keyword_list").split("|")
                for val in keyword_vals:
                    keyword_discriminants.append(val.lower().strip())

            for t in transactions:
                cont = True
                if check_user_discriminants:
                    if not t.recipient in user_discriminants:
                        cont = False
                if cont:
                    if check_keyword_discriminants:
                        lowered = t.description.lower().strip()
                        if self.request.get("description_keyword_search_mode") == "AND":
                            hit_cnt = 0
                            for item in keyword_discriminants:
                                hit_cnt += int(item in lowered)
                            if hit_cnt < len(keyword_discriminants):
                                cont = False
                        elif self.request.get("description_keyword_search_mode") == "OR":
                            found_cnt = 0
                            for item in keyword_discriminants:
                                found_cnt += int(item in lowered)
                            if found_cnt == 0:
                                cont = False

                if cont:
                    item = {"identifier": t.identifier, "dollars": t.dollars, "cents": t.cents, "approved": bool_map[int(t.approved)], "denied": bool_map[int(t.denied)], "recipient": t.recipient, "payout_date": str(t.payout_date), "description": t.description, "is_reimbursement": bool_map[int("reimbursement" in t.description_key.lower())], "image": ""}
                    if item["is_reimbursement"] == "Yes":
                        info = json.loads(t.extra_info)
                        if "file_extension" in info.keys():                            
                            item["image"] = "https://storage.googleapis.com/" + app_identity.get_default_gcs_bucket_name() + "/Images/Receipts/" + t.identifier + "." + info["file_extension"]
                    if not t.recipient in rep_identifiers_to_query:
                        rep_identifiers_to_query.append(t.recipient)

                    data.append(item)

            reps = FieldApplicationUser.query(FieldApplicationUser.identifier.IN(rep_identifiers_to_query))
            for r in reps:
                rep_identifier_name_dict[r.identifier] = r.first_name.strip().title() + " " + r.last_name.strip().title()

            cnt = len(data)
            first_chunks_size = cnt / 1000
            second_chunks_size = cnt % 1000

            cnt2 = 0
            while cnt2 < first_chunks_size:
                start_idx = cnt2 * 1000
                end_idx = start_idx + 1000
                f = GCSLockedFile("/BulkPayrollExports/" + token + "/" + str(cnt2) + ".json")
                f.write(json.dumps(data[start_idx:end_idx]), "application/json", "public-read")
                cnt2 += 1
            
            f = GCSLockedFile("/BulkPayrollExports/" + token + "/" + str(cnt2) + ".json")
            f.write(json.dumps(data[cnt2 * 1000:(cnt2 * 1000) + second_chunks_size]), "application/json", "public-read")

            f2 = GCSLockedFile("/BulkPayrollExports/" + token + "/names.json")
            f2.write(json.dumps(rep_identifier_name_dict), "application/json", "public-read")

            f3 = GCSLockedFile("/BulkPayrollExports/" + token + "/tally.txt")
            f3.write(str(cnt), "text/plain", "public-read")
