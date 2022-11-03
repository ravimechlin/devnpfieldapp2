@staticmethod
def server_log(fn, user_identifier, agent, request):

    req_cpy = {}
    for item in request.keys():
        if not hasattr(request, "__call__"):
            req_cpy[item] = str(request[item])

    ret_json = {}
    ret_json["items"] = []

    date_created = Helpers.pacific_now()

    n = datetime.now()

    gcs_file = GCSLockedFile("/Logs/activity_log_" + user_identifier + "_" + str(n.year) + "_" + str(n.month) + "_" + str(n.day) + "_" + ".txt")
    result = gcs_file.read()

    if not result is None:
        ret_json["items"] = json.loads(result)

        data_to_store = {}
        data_to_store["user_identifier"] = user_identifier
        data_to_store["user_agent"] = agent
        data_to_store["date_created"] = str(date_created)
        data_to_store["function_called"] = fn
        data_to_store["request_dict"] = req_cpy

        ret_json["items"].append(data_to_store)

        gcs_file.write(json.dumps(ret_json["items"]), "text/plain", "public-read")

    else:

        data_to_store = {}
        data_to_store["user_identifier"] = user_identifier
        data_to_store["user_agent"] = agent
        data_to_store["date_created"] = str(date_created)
        data_to_store["function_called"] = fn
        data_to_store["request_dict"] = req_cpy

        ret_json["items"].append(data_to_store)

        gcs_file.write(json.dumps(ret_json["items"]), "text/plain", "public-read")

    return True
