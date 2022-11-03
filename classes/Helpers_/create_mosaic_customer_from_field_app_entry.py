@staticmethod
def create_mosaic_customer_from_field_app_entry(app_entry):
    ip = Helpers.get_mosaic_ip()
    urll = "http://" + ip + "/insert_job.php"

    dct = {}
    dct["token"] = Helpers.guid()
    dct["job_type"] = "create_opportunity"
    dct["identifier"] = dct["token"]
    dct["field_app_data"] = {}
    dct["field_app_data"]["identifier"] = app_entry.identifier
    dct["field_app_data"]["office_identifier"] = app_entry.office_identifier
    dct["field_app_data"]["booking_identifier"] = app_entry.booking_identifier
    dct["field_app_data"]["customer_signature_date"] = str(app_entry.customer_signature_date)
    dct["field_app_data"]["customer_first_name"] = app_entry.customer_first_name
    dct["field_app_data"]["customer_last_name"] = app_entry.customer_last_name
    dct["field_app_data"]["customer_email"] = app_entry.customer_email
    dct["field_app_data"]["customer_phone"] = app_entry.customer_phone
    dct["field_app_data"]["customer_dob"] = str(app_entry.customer_dob)
    dct["field_app_data"]["customer_postal"] = app_entry.customer_postal
    dct["field_app_data"]["customer_city"] = app_entry.customer_city
    dct["field_app_data"]["customer_state"] = app_entry.customer_state
    dct["field_app_data"]["customer_address"] = app_entry.customer_address
    dct["field_app_data"]["customer_cpf_id"] = app_entry.customer_cpf_id
    dct["field_app_data"]["customer_utility_account_number"] = app_entry.customer_utility_account_number
    dct["field_app_data"]["customer_kwh_price"] = app_entry.customer_kwh_price
    dct["field_app_data"]["rep_id"] = app_entry.rep_id
    dct["field_app_data"]["rep_email"] = app_entry.rep_email
    dct["field_app_data"]["actual_email"] = app_entry.customer_email
    dct["field_app_data"]["rep_phone"] = app_entry.rep_phone
    dct["field_app_data"]["rep_lead_id"] = app_entry.rep_lead_id
    dct["field_app_data"]["insert_time"] =app_entry.insert_time
    dct["field_app_data"]["processed"] = app_entry.processed
    dct["field_app_data"]["image_extension"] = app_entry.image_extension
    dct["field_app_data"]["opt_rep_notes"] = app_entry.opt_rep_notes
    dct["field_app_data"]["sp_two_time"] = str(app_entry.sp_two_time)
    dct["field_app_data"]["utility_provider"] = app_entry.utility_provider
    dct["field_app_data"]["customer_mosaic_id"] = app_entry.customer_mosaic_id

    form_fields = {}
    form_fields["json"] = json.dumps(dct)

    resp = urlfetch.fetch(
        url=urll,
            method=urlfetch.POST,
            payload=urllib.urlencode(form_fields),
            deadline=20,
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
    )
    return dct["token"]
