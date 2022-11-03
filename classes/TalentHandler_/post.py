def post(self):
    import base64
    self.response.content_type = "application/json"
    status_msg = {}
    status_msg["success"] = False

    try:
        form_fields = {}
        form_fields["name"] = self.request.get("name")
        form_fields["email"] = self.request.get("email")
        logging.info(form_fields["email"])
        form_fields["expert_in_python"] = (self.request.get("expert_in_python") == "1")
        form_fields["expert_in_js"] = (self.request.get("expert_in_js") == "1")

        if not str(self.request.get("sample_apps_script_code")) == "":
            form_fields["sample_apps_script_code"] = base64.b64decode(self.request.get("sample_apps_script_code"))
        else:
            form_fields["sample_apps_script_code"] = None

        if not str(self.request.get("sample_apps_script_description")) == "":
            form_fields["sample_apps_script_description"] = self.request.get("sample_apps_script_description")
        else:
            form_fields["sample_apps_script_description"] = None

        if not str(self.request.get("app_engine_url")) == "":
            form_fields["app_engine_url"] = self.request.get("app_engine_url")
        else:
            form_fields["app_engine_url"] = None

        key = Helpers.guid()
        form_fields["link_to_pdf"] = "https://storage.googleapis.com/" + app_identity.get_default_gcs_bucket_name() + "/Talent/PDFS/" + key + ".pdf"
        pdf_content = self.request.POST.multi['resume'].file.read()

        bucket_name = os.environ.get('BUCKET_NAME',
                             app_identity.get_default_gcs_bucket_name())

        bucket = '/' + bucket_name
        filename = bucket + '/Talent/PDFS/' + key + '.pdf'

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(
                        filename,
                        'w',
                        content_type="application/pdf",
                        options={'x-goog-meta-foo': 'foo',
                                'x-goog-meta-bar': 'bar',
                                'x-goog-acl': 'public-read'},
                        retry_params=write_retry_params)
        gcs_file.write(pdf_content)
        gcs_file.close()

        filename = bucket + "/Talent/" + key + ".json"
        gcs_file = gcs.open(
            filename,
            'w',
            content_type="application/json",
            options={'x-goog-meta-foo': 'foo',
                     'x-goog-meta-bar': 'bar',
                     'x-goog-acl': 'public-read'},
            retry_params=write_retry_params
        )
        gcs_file.write(json.dumps(form_fields))
        gcs_file.close()

        status_msg["success"] = True
    except:
        self.response.content_type = self.response.content_type

    self.response.out.write(json.dumps(status_msg))

