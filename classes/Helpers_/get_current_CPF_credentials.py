@staticmethod
def get_current_CPF_credentials():
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    filename = bucket + '/ApplicationSettings/cpf_info_' + app_identity.get_application_id() + '.txt'

    credsRetryParams = gcs.RetryParams(initial_delay=0.2,
                                       max_delay=5.0,
                                       backoff_factor=2,
                                       max_retry_period=15,
                                       urlfetch_timeout=30)

    gcs_file = gcs.open(filename, 'r', retry_params=credsRetryParams)

    b64_content = gcs_file.read()
    gcs_file.close()
    jaysawn = Helpers.decrypt(b64_content)
    return json.loads(jaysawn)

