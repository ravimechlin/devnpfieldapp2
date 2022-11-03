def get(self, app_identifier):    
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == app_identifier)
    if not app_entry is None:
        bundle_key = "rep_sales_docs"
        if len(str(self.request.get("bundle_key"))) > 4:
            bundle_key = self.request.get("bundle_key")
        try:
            self.session = get_current_session()
        except:
            self.response.out.write("You are not signed in with your rep credentials.")
            return        

        if bundle_key == "rep_sales_docs":
            existing_viewed_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "docs_viewed_ts_" + app_identifier)
            if existing_viewed_kv is None:
                existing_viewed_kv = KeyValueStoreItem(
                    identifier=Helpers.guid(),
                    keyy="docs_viewed_ts_" + app_identifier,
                    expiration=Helpers.pacific_now() + timedelta(days=7)
                )
            existing_viewed_kv.val = str(Helpers.pacific_now()).split(".")[0]
            existing_viewed_kv.put()


        booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
        if not booking is None:
            proposal = CustomerProposalInfo.first(CustomerProposalInfo.field_app_identifier == app_entry.identifier)
            if proposal is None:
                proposal = CustomerProposalInfo(
                    identifier=Helpers.guid(),
                    field_app_identifier=app_identifier,
                    version=1
                )
                inf_dict = {}
                inf_dict["system_size"] = "0"
                inf_dict["panel_type"] = ""
                inf_dict["panel_qty"] = "0"
                inf_dict["new_panel_qty"] = "0"
                inf_dict["inverter_type"] = ""
                inf_dict["racking"] = ""
                proposal.info = json.dumps(inf_dict)
                
            rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
            if not rep is None:
                template_items = {}
                template_items["rep_name"] = rep.first_name.strip().title() + " " + rep.last_name.strip().title()
                template_items["rep_first_name"] = rep.first_name.strip()
                template_items["customer_name"] = app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
                template_items["customer_first_name"] = app_entry.customer_first_name.strip().title()
                template_items["docs"] = []
                template_items["app_entry_identifier"] = app_identifier
                docs = ComposedDocument.query(
                    ndb.AND
                    (
                        ComposedDocument.bundle_key == bundle_key,
                        ComposedDocument.displayed == True
                    )
                )
                doc_items = []
                for doc in docs:
                    doc_items.append(doc)

                doc_items = Helpers.bubble_sort(doc_items, "idx")
                docs = doc_items

                app_entry_ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
                market_ol = None
                if not app_entry_ol is None:
                    market_ol = OfficeLocation.first(OfficeLocation.identifier == app_entry_ol.parent_identifier)

                supplement_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "secondary_fund_" + app_entry.identifier)
                if not supplement_kv is None:
                    setattr(booking, "secondary_fund", supplement_kv.val)
                for doc in docs:
                    roof_work_item = RoofWorkItem.first(RoofWorkItem.field_app_identifier == app_entry.identifier)
                    if not roof_work_item is None:
                        roof_info = json.loads(roof_work_item.info)                        
                        setattr(app_entry, "reroof_type", roof_info["rep_selection_one"])
                        setattr(app_entry, "reroof_doc_type", roof_info["roof_type"])

                    fn = Helpers.compile_document_formula(json.loads(doc.criteria)["formula"])
                    if fn["fn"](app_entry, booking, proposal, market_ol):
                        template_items["docs"].append({"identifier": doc.identifier, "items": json.loads(doc.template_items), "token": doc.token, "page_count": doc.page_count, "name": doc.name})

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
                
                for doc in other_docs:
                    if is_subscribed:
                        if subscribed_price > 0:
                            template_items["docs"].append({"identifier": doc.identifier, "items": json.loads(doc.template_items), "token": doc.token, "page_count": doc.page_count, "name": doc.name})


                if app_entry.utility_provider == "southern_california_edison":
                    proposal.fix_additional_amount()
                    proposal.fix_system_size()
                    info3 = json.loads(proposal.info)
                    if float(info3["system_size"]) < 10.0:
                        edison_doc = ComposedDocument.first(ComposedDocument.name == "SCE Under 10KW")
                        if not edison_doc is None:
                            obj5 = {"identifier": edison_doc.identifier, "items": json.loads(edison_doc.template_items), "token": edison_doc.token, "page_count": edison_doc.page_count, "name": edison_doc.name}
                            template_items["docs"].append(obj5)
                    else:
                        edison_doc = ComposedDocument.first(ComposedDocument.name == "SCE Over 10KW")
                        if not edison_doc is None:
                            obj5 = {"identifier": edison_doc.identifier, "items": json.loads(edison_doc.template_items), "token": edison_doc.token, "page_count": edison_doc.page_count, "name": edison_doc.name}
                            template_items["docs"].append(obj5)

                cs_kv1 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "cosigner_name_" + app_entry.identifier)
                if cs_kv1 is None:                    
                    d_tally = 0
                    for d in template_items["docs"]:
                        o_tally = 0
                        for obj in d["items"]:
                            filtered_items = []
                            for it in obj:
                                if it["value"] == "cosigner_signature" or it["value"] == "cosigner_initials" or it["value"] == "cosigner_name":
                                #skip
                                    x = 5
                                else:
                                    filtered_items.append(it)

                            template_items["docs"][d_tally]["items"][o_tally] = json.loads(json.dumps(filtered_items))
                            o_tally += 1
                            obj = json.loads(json.dumps(filtered_items))

     

                        d_tally += 1
                    
               
                template_items["docs"] = json.dumps(template_items["docs"])         
                f = GCSLockedFile("/debugging/test332.json")
                f.write(template_items["docs"], "application/json", "public-read")
                f.unlock()


                path = Helpers.get_html_path('sign.html')
                if bundle_key == "sales_form":
                    path = Helpers.get_html_path("sign_sales_form.html")
                elif bundle_key == "roof_work":
                    path = Helpers.get_html_path("sign_roof_work.html")
                self.response.out.write(template.render(path, template_items))

    else:
        pending_user_identifier = app_identifier
        kv_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "new_user_registration_" + pending_user_identifier)
        if not kv_item is None:
            bundle_key = "rep_employment_docs"
            if len(str(self.request.get("bundle_key"))) > 4:
                bundle_key = self.request.get("bundle_key")

            pending_user = json.loads(kv_item.val)
            template_items = {}
            template_items["pending_user_identifier"] = pending_user_identifier
            template_items["rep_name"] = pending_user["user_first"].strip().title() + " " + pending_user["user_last"].strip().title()
            template_items["rep_first_name"] = pending_user["user_first"].strip().title()
            template_items["docs"] = []
            docs = ComposedDocument.query(ComposedDocument.bundle_key == bundle_key)
            doc_items = []
            for doc in docs:
                doc_items.append(doc)
            doc_items = Helpers.bubble_sort(doc_items, "idx")
            docs = doc_items
            for doc in docs:
                fn = Helpers.compile_document_formula(json.loads(doc.criteria)["formula"], True)
                if fn["fn"](pending_user):
                    template_items["docs"].append({"identifier": doc.identifier, "items": json.loads(doc.template_items), "token": doc.token, "page_count": doc.page_count, "name": doc.name})

            template_items["docs"] = json.dumps(template_items["docs"])
            path = Helpers.get_html_path('sign_rep.html')
            self.response.out.write(template.render(path, template_items))


