def campaign_jobs(self):
    import json
    import cloudstorage as gcs
    from google.appengine.api import app_identity
    import os

    now = Helpers.pacific_now()
    file_name = "/CampaignJobs/" + str(now.year) + "_" + str(now.month) + "_" + str(now.day) + "_" + str(now.hour) + "_jobs.json"
    f = GCSLockedFile(file_name)
    content = f.read()
    app_ids_sent = []
    phone_numbers_sent = []
    if not content is None:
        data = json.loads(f.read())

        for item in data:
            app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == item["field_app_identifier"])
            rep = FieldApplicationUser.first(FieldApplicationUser.identifier == item["rep_identifier"])
            if (not app_entry is None) and (not rep is None) and (not item["field_app_identifier"] in app_ids_sent) and (not app_entry.customer_phone in phone_numbers_sent):
                Helpers.mms_campaign(item["key"], app_entry, rep)
                app_ids_sent.append(item["field_app_identifier"])
                phone_numbers_sent.append(app_entry.customer_phone)

        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        filename2 = bucket + file_name
        gcs.delete(filename2)
