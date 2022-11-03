def get(self):
    time.sleep(1)
    self.response.content_type = "application/json"
    oset = None
    oset2 = None
    offset_param = "offset"
    if str(self.request.get("offset")) == "" or str(self.request.get("offset")).lower() == "none":
        oset = 0
    else:
        oset = int(self.request.get("offset"))

    if str(self.request.get("offset2")) == "" or str(self.request.get("offset2")).lower() == "none":
        oset2 = 0
        if oset == 0:
            offset_param = "offset2"
    else:
        oset2 = int(self.request.get("offset2"))
        offset_param = "offset2"

    token = None
    if str(self.request.get("token")) == "" or str(self.request.get("token")).lower() == "none":
        offset_param = "offset"
        token = hashlib.md5(Helpers.guid()).hexdigest()
    else:
        token = self.request.get("token")

    no_data_left = True
    no_data_left2 = True
    custs = FieldApplicationEntry.query().order(FieldApplicationEntry.insert_time)
    data_to_put = []
    if offset_param == "offset":
        for cust in custs.fetch(50, offset=oset):
            no_data_left = False
            data_item = {}
            data_item["identifier"] = cust.identifier
            data_item["first_name"] = cust.customer_first_name
            data_item["last_name"] = cust.customer_last_name
            data_item["spouse"] = cust.spouse_name
            data_item["spouse_name"] = cust.spouse_name
            data_item["rep_id"] = cust.rep_id
            data_item["archived"] = cust.archived
            data_item["save_me"] = cust.save_me
            data_to_put.append(data_item)

    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    filename = bucket + '/TempSearchDocs/' + token + '.json'
    retryParameters = gcs.RetryParams(initial_delay=0.2,
                                        max_delay=5.0,
                                        backoff_factor=2,
                                        max_retry_period=15,
                                        urlfetch_timeout=30)

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)

    try:
        if len(data_to_put) > 0:

            prev_data = None

            if oset > 0:
                gcs_file1 = gcs.open(filename, 'r', retry_params=retryParameters)
                prev_data = json.loads(gcs_file1.read())
                gcs_file1.close()
            else:
                prev_data = []

            new_data = prev_data + data_to_put

            gcs_file2 = gcs.open(
                filename,
                'w',
                content_type="text/plain",
                options={'x-goog-meta-foo': 'foo',
                            'x-goog-meta-bar': 'bar',
                            'x-goog-acl': 'public-read'},
                retry_params=write_retry_params
            )

            gcs_file2.write(json.dumps(new_data))
            gcs_file2.close()

        else:
            index = search.Index(name="cust_names")
            if oset2 == 0:
                try:
                    while True:
                        # Get a list of documents populating only the doc_id field and extract the ids.
                        document_ids = [document.doc_id
                        for document in index.get_range(ids_only=True)]

                        if not document_ids:
                            break

                        # Delete the documents for the given ids from the Index.
                        index.delete(document_ids)
                except:
                    logging.info("hit exception 1")
                    index = search.Index(name="cust_names")

            gcs_file1 = gcs.open(filename, 'r', retry_params=retryParameters)
            full_data = json.loads(gcs_file1.read())
            gcs_file1.close()
            #gcs.delete(filename)

            docs_to_put = []
            count = oset2
            loop_cnt = 0
            while (count < len(full_data)) and loop_cnt < 50:
                no_data_left2 = False
                item = full_data[count]
                fnames = item["first_name"].lower()
                fname_str = ""
                for fname in fnames.split(" "):
                    fnayme = ""
                    if len(fname) > 0:
                        fnayme = str(fname[0]).upper() + fname[1:]
                    else:
                        fnayme = fname.upper()

                    fname_str += (fnayme + " ")

                fname_str = fname_str[0:-1]

                lnames = item["last_name"].lower()
                lname_str = ""
                for lname in lnames.split(" "):
                    lnayme = ""
                    if len(lname) > 0:
                        lnayme = str(lname[0]).upper() + lname[1:]
                    else:
                        lnayme = lname.upper()

                    lname_str += (lnayme + " ")

                lname_str = lname_str[0:-1]

                name_title_cased = fname_str + " " + lname_str
                spouse_name_title_cased = "n/a"
                if not item["spouse_name"] == "n/a":
                    fnames2 = item["spouse_name"].lower()
                    fname_str2 = ""
                    for fname2 in fnames2.split(" "):
                        fnayme2 = ""
                        if len(fname2) > 0:
                            fnayme2 = str(fname2[0]).upper() + fname2[1:]
                        else:
                            fnayme2 = fname2.upper()

                        fname_str2 += (fnayme2 + " ")

                    fname_str2 = fname_str2[0:-1]

                    lnames2 = item["last_name"].lower()
                    lname_str2 = ""
                    for lname2 in lnames2.split(" "):
                        lnayme2 = ""
                        if len(lname2) > 0:
                            lnayme2 = str(lname2[0]).upper() + lname2[1:]
                        else:
                            lnayme2 = lname2.upper()

                        lname_str2 += (lnayme2 + " ")

                    lname_str2 = lname_str2[0:-1]

                    spouse_name_title_cased = fname_str2 + " " + lname_str2

                docs_to_put.append(
                    search.Document(
                        fields=[
                            search.TextField(name="cust_identifier", value=item["identifier"]),
                            search.TextField(name="cust_name", value=item["first_name"] + " " + item["last_name"]),
                            search.TextField(name="cust_name_l", value=item["first_name"].lower() + " " + item["last_name"].lower()),
                            search.TextField(name="cust_name_title_case", value=name_title_cased),
                            search.TextField(name="rep_id", value=item["rep_id"]),
                            search.TextField(name="spouse", value=spouse_name_title_cased)
                        ]
                    )
                )
                count += 1
                loop_cnt += 1

            index.put(docs_to_put)


    except:
        logging.info("hit exception 2")
        token = token

    ret_json = {}
    ret_json["done"] = no_data_left and no_data_left2
    ret_json["offset_param"] = "offset"
    if not ret_json["done"]:
        base = oset
        if no_data_left and (not no_data_left2):
            base = oset2
            ret_json["offset_param"] = "offset2"

        ret_json["next_request"] = {}
        ret_json["next_request"]["token"] = token
        ret_json["next_request"]["offset"] = base + 50


    self.response.out.write(json.dumps(ret_json))
