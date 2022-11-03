from google.appengine.api import app_identity

def get_default_gcs_bucket_name():
    app_id = app_identity.get_application_id() + ".appspot.com"

    if app_identity.get_application_id() in ["lojixonpfieldapp", "mwnpfieldapp"]:
        return app_id.replace(".", "_")

    return app_id

