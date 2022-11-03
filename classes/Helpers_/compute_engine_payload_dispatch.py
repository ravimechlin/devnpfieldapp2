@staticmethod
def compute_engine_payload_dispatch(ip, port, path, http_method, data, production_flag):
    from google.appengine.api import app_identity
    headerss = {}

    you_r_l = "http://" + ip + ":" + str(port) + "/" + path
    if http_method == "GET":
        you_r_l += Helpers.data_dict_to_url_params(data)
        headerss[str('Content-Type')] = str('text/html')
    elif http_method == "POST":
        headerss[str('Content-Type')] = str('application/x-www-form-urlencoded')

    if production_flag:
        headerss[str('Cookie')] = 'mode=prod'
    if app_identity.get_application_id() == "devnpfieldapp2":
        headerss[str('Cookie')] = 'mode=dev2'

    resp = None
    if http_method == "POST":
        resp = urlfetch.fetch(
            url=you_r_l,
            method=urlfetch.POST,
            payload=urllib.urlencode(data),
            deadline=45,
            headers=headerss
        )
    else:
        resp = urlfetch.fetch(
            url=you_r_l,
            method=urlfetch.GET,
            deadline=45,
            headers=headerss

        )

    return resp.content


