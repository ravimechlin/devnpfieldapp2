@staticmethod
def get_credit_request_xml_body(mode="prod", app_entry=None, social_security=None):
    if app_entry is None:
        app_entry = FieldApplicationEntry.first(
            ndb.AND(FieldApplicationEntry.customer_first_name == "Raymond",
                    FieldApplicationEntry.customer_address == "657 Occidental Dr")
        )

    if social_security is None:
        social_security = "666125812"
    vals_dict = {}
    vals_dict["user_ref_number"] = "0123456789"
    vals_dict["processing_environment"] = ""
    vals_dict["password"] = ""
    vals_dict["first"] = ""
    vals_dict["last"] = ""
    vals_dict["address"] = ""
    vals_dict["city"] = ""
    vals_dict["ss_num"] = social_security

    if mode == "prod":
        vals_dict["processing_environment"] = "production"
        vals_dict["password"] = "XAD5"
        vals_dict["first"] = app_entry.customer_first_name.strip().upper()
        vals_dict["last"] = app_entry.customer_last_name.strip().upper()

        vals_dict["address"] = app_entry.customer_address.strip().upper()
        vals_dict["city"] = app_entry.customer_city.strip().upper()
        vals_dict["state"] = app_entry.customer_state
        vals_dict["postal"] = app_entry.customer_postal

        dob = str(app_entry.customer_dob)
        if " " in dob:
            dob = dob.split(" ")[0]
        vals_dict["dob"] = dob


    else:
        vals_dict["processing_environment"] = "standardTest"
        vals_dict["password"] = "PSWD"
        vals_dict["first"] = "ZELNINO"
        vals_dict["last"] = "WINTER"
        vals_dict["number"] = "760"
        vals_dict["address"] = "760 W. SPROUL RD"
        vals_dict["city"] = "FANTASY ISLAND"
        vals_dict["state"] = "IL"
        vals_dict["postal"] = "60750"
        vals_dict["dob"] = "1967-04-17"

    xml = '''<?xml version="1.0"?> <creditBureau xmlns="http://www.transunion.com/namespace" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> <document>request</document> <version>2.8</version> <transactionControl> <userRefNumber>{{user_ref_number}}</userRefNumber> <subscriber> <industryCode>U</industryCode> <memberCode>01151262</memberCode> <inquirySubscriberPrefixCode>1201</inquirySubscriberPrefixCode> <password>{{password}}</password> </subscriber> <options> <processingEnvironment>{{processing_environment}}</processingEnvironment> <country>us</country> <language>en</language> <contractualRelationship>individual</contractualRelationship> <pointOfSaleIndicator>none</pointOfSaleIndicator> </options> </transactionControl> <product> <code>07000</code> <subject> <number>1</number> <subjectRecord> <indicative> <name> <person> <first>{{first}}</first> <last>{{last}}</last> </person> </name> <address> <status>current</status> <street> <unparsed>{{address}}</unparsed> </street> <location> <city>{{city}}</city> <state>{{state}}</state> <zipCode>{{postal}}</zipCode> </location> </address> <socialSecurity> <number>{{ss_num}}</number> </socialSecurity> <dateOfBirth>{{dob}}</dateOfBirth> </indicative> <addOnProduct> <code>00P02</code> <scoreModelProduct>true</scoreModelProduct> </addOnProduct> </subjectRecord> </subject> <responseInstructions> <returnErrorText>true</returnErrorText> <document/> </responseInstructions> <permissiblePurpose> <inquiryECOADesignator>individual</inquiryECOADesignator> </permissiblePurpose> </product> </creditBureau>'''

    for val in vals_dict.keys():
        xml = xml.replace("{{" + val + "}}", vals_dict[val])

    return xml

