def get_payment_customizations_for_user(self):
    self.response.content_type = "application/json"
    ret_json = {}
    ret_json["price_per_hk"] = None
    kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pay_per_hk_" + self.request.get("identifier"))
    if not kv is None:
        ret_json["price_per_hk"] = kv.val
    ret_json["install_pay"] = None
    kv2 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pay_per_install_" + self.request.get("identifier"))
    if not kv2 is None:
        ret_json["install_pay"] = kv2.val
    ret_json["install_per_kw_pay"] = None
    kv3 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pay_per_install_per_kw_" + self.request.get("identifier"))
    if not kv3 is None:
        ret_json["install_per_kw_pay"] = kv3.val

    ret_json["commission_per_self_gen_sale"] = None
    kv4 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "commission_per_self_gen_sale_" + self.request.get("identifier"))
    if not kv4 is None:
        ret_json["commission_per_self_gen_sale"] = kv4.val

    ret_json["commission_per_lead_sale"] = None
    kv5 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "commission_per_lead_sale_" + self.request.get("identifier"))
    if not kv5 is None:
        ret_json["commission_per_lead_sale"] = kv5.val

    pricing_structures = Helpers.get_pricing_structures()
    user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.request.get("identifier"))
    if not user is None:
        if user.user_type in ["solar_pro", "solar_pro_manager"]:
            office = OfficeLocation.first(OfficeLocation.identifier == user.main_office)
            if not office is None:
                market_key = office.parent_identifier
                if market_key in pricing_structures.keys():
                    if ret_json["price_per_hk"] is None:
                        price_per_hk_keys = ["solar_pro_pay_per_hk", "solar_pro_manager_pay_per_hk"]
                        key = price_per_hk_keys[int(user.user_type == "solar_pro_manager")]
                        if key in pricing_structures[market_key].keys():
                            ret_json["price_per_hk"] = str(pricing_structures[market_key][key])

                    if ret_json["install_pay"] is None:
                        install_pay_keys = ["solar_pro_flat_amount_per_install", "solar_pro_manager_flat_amount_per_install"]
                        key = install_pay_keys[int(user.user_type == "solar_pro_manager")]
                        if key in pricing_structures[market_key].keys():
                            ret_json["install_pay"] = str(pricing_structures[market_key][key])

                    if ret_json["install_per_kw_pay"] is None:
                        per_kw_keys = ["solar_pro_per_kw_amount_per_install", "solar_pro_manager_per_kw_amount_per_install"]
                        key = per_kw_keys[int(user.user_type == "solar_pro_manager")]
                        if key in pricing_structures[market_key].keys():
                            ret_json["install_per_kw_pay"] = str(pricing_structures[market_key][key])

        elif user.user_type in ["sales_manager", "energy_expert"]:
            office = OfficeLocation.first(OfficeLocation.identifier == user.main_office)
            if not office is None:
                market_key = office.parent_identifier
                if market_key in pricing_structures.keys():
                    if ret_json["commission_per_self_gen_sale"] is None:
                        self_gen_keys = ["energy_expert_self_gen_commission_per_kw", "sales_manager_self_gen_commission_per_kw"]
                        key = self_gen_keys[int(user.user_type == "sales_manager")]
                        if key in pricing_structures[market_key].keys():
                            ret_json["commission_per_self_gen_sale"] = str(pricing_structures[market_key][key])

                    if ret_json["commission_per_lead_sale"] is None:
                        lead_keys = ["energy_expert_commission_per_kw", "sales_manager_commission_per_kw"]
                        key = lead_keys[int(user.user_type == "sales_manager")]
                        if key in pricing_structures[market_key].keys():
                            ret_json["commission_per_lead_sale"] = str(pricing_structures[market_key][key])

        

    self.response.out.write(json.dumps(ret_json))
