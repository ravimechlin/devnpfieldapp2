def sign_docs(self):
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    from google.appengine.api import taskqueue

    token = hashlib.md5(Helpers.guid()).hexdigest()
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == self.request.get("identifier"))
    user_kv_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "new_user_registration_" + self.request.get("identifier"))
    if not app_entry is None:
        roof_work_item = RoofWorkItem.first(RoofWorkItem.field_app_identifier == app_entry.identifier)
        
        
        if not roof_work_item is None:
            roof_info = json.loads(roof_work_item.info)                        
            setattr(app_entry, "reroof_type", roof_info["rep_selection_one"])
            setattr(app_entry, "reroof_doc_type", roof_info["roof_type"])

        booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
        if not booking is None:
            supplement_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "secondary_fund_" + app_entry.identifier)
            if not supplement_kv is None:
                setattr(booking, "secondary_fund", supplement_kv.val)

            
            proposal = CustomerProposalInfo.first(CustomerProposalInfo.field_app_identifier == self.request.get("identifier"))
            if not proposal is None:
                proposal.fix_system_size()
                proposal.fix_additional_amount()

            rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
            if not rep is None:
                user_sig = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "customer_signature_" + app_entry.identifier)
                if user_sig is None:
                    user_sig = KeyValueStoreItem(
                        val="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                    )
                user_initials = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "customer_initials_" + app_entry.identifier)
                if user_initials is None:
                    user_initials = KeyValueStoreItem(
                        val="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                    )
                if not user_initials is None or 999 == 999:
                    logging.info("GG")
                    incentive_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "incentive_option_" + app_entry.identifier)
                    if incentive_kv is None:
                        incentive_kv = KeyValueStoreItem(
                            val=""
                        )

                    if not incentive_kv is None:
                        utility_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "utility_person_" + app_entry.identifier)
                        if utility_kv is None:
                            utility_kv = KeyValueStoreItem(
                                val=""
                            )
                        if not utility_kv is None:
                            greensky_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "is_greensky_" + app_entry.identifier)
                            if greensky_kv is None:
                                greensky_kv = KeyValueStoreItem(
                                    val=""
                                )
                            if not greensky_kv is None:
                                logging.info("HH")
                                greensky = (greensky_kv.val == "1")
                                acct_num = ""
                                exp_year = ""
                                exp_month = ""
                                cvv_num = ""
                                if greensky:
                                    mapping = {
                                        "credit_card_number_" + app_entry.identifier: acct_num,
                                        "credit_card_expiration_month_" + app_entry.identifier: exp_month,
                                        "credit_card_expiration_year_" + app_entry.identifier: exp_year,
                                        "credit_card_cvv_num_" + app_entry.identifier: cvv_num
                                    }
                                    kv_items = KeyValueStoreItem.query(KeyValueStoreItem.keyy.IN(mapping.keys()))
                                    hit_cnt = 0
                                    for kv_item66 in kv_items:
                                        mapping[kv_item66.keyy] = kv_item66.val
                                        hit_cnt += 1

                                bundle_key = "rep_sales_docs"
                                if len(str(self.request.get("bundle_key"))) > 4:
                                    bundle_key = self.request.get("bundle_key")
                                docs = ComposedDocument.query(ComposedDocument.bundle_key == bundle_key)
                                doc_items = []
                                for doc in docs:
                                    doc_items.append(doc)

                                doc_items = Helpers.bubble_sort(doc_items, "idx")

                                qualified_documents = []
                                app_entry_ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
                                market_ol = None
                                if not app_entry_ol is None:
                                    market_ol = OfficeLocation.first(OfficeLocation.identifier == app_entry_ol.parent_identifier)

                                other_docs = ComposedDocument.query(ComposedDocument.name.IN(["Blank", "Customer Service Plan"]))   
                                svc_file = GCSLockedFile("/CustomerService/bulk.json")
                                svc_contents = svc_file.read()
                                svc_file.unlock()
                                if svc_contents is None:
                                    svc_contents = "[]"

                                deserialized_svc = json.loads(svc_contents)
                                is_subscribed = False
                                subscribed_price = 0
                                for item in deserialized_svc:
                                    if item["field_app_identifier"] == app_entry.identifier:
                                        is_subscribed = True
                                        subscribed_price = int(item["price"])
                                
                                other_doc_identifier = None
                                for doc in other_docs:
                                    if is_subscribed:
                                        if subscribed_price > 0:
                                            doc_items.append(doc)
                                            other_doc_identifier = doc.identifier

                                for doc in doc_items:
                                    
                                    
                                    fn = Helpers.compile_document_formula(json.loads(doc.criteria)["formula"])
                                    if fn["fn"](app_entry, booking, proposal, market_ol) or doc.identifier == other_doc_identifier:
                                            qualified_documents.append(doc.identifier)
                                            if greensky:
                                                Helpers.populate_document_v2(user_sig.val, user_initials.val, doc, app_entry, booking, proposal, token, rep, incentive_kv.val, utility_kv.val, mapping["credit_card_number_" + app_entry.identifier], mapping["credit_card_expiration_year_" + app_entry.identifier], mapping["credit_card_expiration_month_" + app_entry.identifier], mapping["credit_card_cvv_num_" + app_entry.identifier])
                                            else:
                                                Helpers.populate_document_v2(user_sig.val, user_initials.val, doc, app_entry, booking, proposal, token, rep, incentive_kv.val, utility_kv.val)


                                if app_entry.utility_provider == "southern_california_edison":
                                    proposal.fix_additional_amount()
                                    proposal.fix_system_size()
                                    info3 = json.loads(proposal.info)
                                    if float(info3["system_size"]) < 10.0:
                                        edison_doc = ComposedDocument.first(ComposedDocument.name == "SCE Under 10KW")
                                        if not edison_doc is None:
                                            Helpers.populate_document_v2(user_sig.val, user_initials.val, edison_doc, app_entry, booking, proposal, token, rep, incentive_kv.val, utility_kv.val)
                                    else:
                                        edison_doc = ComposedDocument.first(ComposedDocument.name == "SCE Over 10KW")
                                        if not edison_doc is None:
                                            Helpers.populate_document_v2(user_sig.val, user_initials.val, edison_doc, app_entry, booking, proposal, token, rep, incentive_kv.val, utility_kv.val)

                                from google.appengine.api import taskqueue
                                identifier = self.request.get("identifier")                                            
                                usr = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
                                if not usr is None:
                                    x = 5
                                    #CustomerTranscriber.transcribe(app_entry, usr, "customer_signs_docs_end")
                                    if bundle_key == "rep_sales_docs":
                                        app_entry.deal_locked = True
                                        app_entry.put()

                                        ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
                                        if not ol is None:
                                            market_key = ol.parent_identifier
                                            prop_info = json.loads(proposal.info)
                                            pricing_structures = Helpers.get_pricing_structures()
                                            funds = Helpers.list_funds()
                                            s_cost = round(float(Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, prop_info, pricing_structures, funds)), 2)
                                            
                                            s_cost_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "total_system_cost_" + app_entry.identifier)
                                            if s_cost_kv is None:
                                                s_cost_kv = KeyValueStoreItem(
                                                    identifier=Helpers.guid(),
                                                    keyy="total_system_cost_" + app_entry.identifier,                                                    
                                                    expiration=datetime(1970, 1, 1)
                                                )
                                            s_cost_kv.val = str(s_cost)
                                            s_cost_kv.put()
                        
                                    taskqueue.add(url="/tq/mail_signed_docs", params={"identifier": identifier, "token": token, "bundle_key": str(self.request.get("bundle_key"))})

    elif (not user_kv_item is None):
        pending_user = json.loads(user_kv_item.val)
        user_sig = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pending_user_signature_" + self.request.get("identifier"))
        if not user_sig is None:
            bundle_key = "rep_employment_docs"
            if len(str(self.request.get("bundle_key"))) > 4:
                bundle_key = self.request.get("bundle_key")
            docs = ComposedDocument.query(ComposedDocument.bundle_key == bundle_key)
            doc_items = []
            for doc in docs:
                doc_items.append(doc)

            doc_items = Helpers.bubble_sort(doc_items, "idx")


            for doc in doc_items:
                fn = Helpers.compile_document_formula(json.loads(doc.criteria)["formula"], True)
                if fn["fn"](pending_user):
                    Helpers.populate_rep_document(user_sig.val, doc, token, pending_user)

            from google.appengine.api import taskqueue
            identifier = self.request.get("identifier")
            taskqueue.add(url="/tq/mail_signed_docs", params={"identifier": identifier, "token": token, "bundle_key": str(self.request.get("bundle_key"))})
