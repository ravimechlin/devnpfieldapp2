def post(self):
    self.session = get_current_session()

    category = self.request.get("cat_sel")
    amt = float(self.request.get("amnt_in_val").replace(",", "").replace("$", ""))
    description = self.request.get("reimbursement_desc_val") + ": " + self.request.get("reimbursement_desc")

    recip = -5
    try:
        recip = self.session["user_identifier"]
    except:
        if len(str(self.request.get("recipient_identifier"))) == 128:
            recip = str(self.request.get("recipient_identifier"))

    dollars = int(amt)
    cents = int((amt * 100) % 100)

    folder_name_temp = category.split("_")
    folder_name_1 = folder_name_temp[0]
    folder_name_2 = folder_name_temp[1]
    folder = folder_name_1[0].upper() + folder_name_1[1:] + folder_name_2[0].upper() + folder_name_2[1:]

    file_content = None
    pic_name = None
    name_element = None
    pic_type = None
    pic_ext = None
    pic_mime = None
    extra_info_dct = None
    extra_info = None
    if (not str(self.request.get("admin_qualifier")) == "1") or str(self.request.get("has_file")) == "1":
        file_content = self.request.POST.multi['pic'].file.read()
        pic_name = self.request.params["pic"].filename.lower()
        name_elements = pic_name.split(".")
        pic_type = name_elements[len(name_elements) - 1]
        pic_ext = ""
        pic_mime = ""
        if pic_type == "png":
            pic_ext = "png"
            pic_mime = "image/png"
        else:
            pic_ext = "jpg"
            pic_mime = "image/jpg"

    else:
        pic_ext = "jpg"
        pic_mime = "image/jpg"

    extra_info_dct = {}
    extra_info_dct["file_extension"] = pic_ext
    extra_info = json.dumps(extra_info_dct)


    c_num = "-1"

    transaction_id = Helpers.guid()
    payout_date = Helpers.upcoming_friday()
    h_p_t = Helpers.pacific_today()
    if not h_p_t.isoweekday() in [1, 2, 6, 7]:
        payout_date =  payout_date + timedelta(days=7)

    if str(self.request.get("admin_qualifier")) == "1":
        pd_vals = str(self.request.get("payout_date")).split("-")
        payout_date = date(int(pd_vals[0]), int(pd_vals[1]), int(pd_vals[2]))

    reimbursement_request = MonetaryTransactionV2(
        identifier=transaction_id,
        description=str(description),
        description_key=category,
        created=Helpers.pacific_now(),
        paid=False,
        recipient=self.session["user_identifier"],
        dollars=dollars,
        cents=cents,
        check_number=-1,
        approved=False,
        denied=False,
        field_app_identifier="n/a",
        extra_info=extra_info,
        payout_date=payout_date
    )
    if str(self.request.get("admin_qualifier")) == "1":
        reimbursement_request.approved = True
        reimbursement_request.denied = False
        reimbursement_request.recipient = self.request.get("recipient")
    
    reimbursement_request.put()
    #s_index = search.Index(name="v2_transactions")
    #s_index.put(
    #    [search.Document(
    #        fields=[
    #            search.TextField(name="identifier", value=reimbursement_request.identifier),
    #            search.TextField(name="description", value=reimbursement_request.description)
    #        ]
    #    )]
    #)

    new_name = hashlib.md5(str(transaction_id)).hexdigest()

    if not file_content is None:
        bucket_name = os.environ.get('BUCKET_NAME',
            app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        filename = bucket + "/Images/Receipts/" + transaction_id + "." + pic_ext

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(filename,
                            'w',
                            content_type=pic_mime,
                            options={'x-goog-meta-foo': 'foo',
                                    'x-goog-meta-bar': 'bar',
                                    'x-goog-acl': 'public-read'},
                            retry_params=write_retry_params)
        gcs_file.write(file_content)
        gcs_file.close()        
    else:
        Helpers.gcs_copy("/Images/Receipts/missing_receipt.jpg", "Images/Receipts/" + transaction_id + ".jpg", "image/jpg", "public-read")

    self.redirect("/rep")

