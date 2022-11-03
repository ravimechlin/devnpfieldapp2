def address_search_field_init(self):
    from google.appengine.api import search
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.sp_two_time >= Helpers.pacific_now() + timedelta(days=-365))
    index = search.Index(name="cust_addies2")
    lst = []
    docs_to_put = []
    for app_entry in app_entries:

        docs_to_put.append(
            search.Document(
                fields=[
                    search.TextField(name="identifier", value=app_entry.identifier),
                    search.TextField(name="cust_address", value=app_entry.customer_address),
                    search.TextField(name="cust_city_state", value=app_entry.customer_city + ", " + app_entry.customer_state),
                    search.TextField(name="cust_postal", value=app_entry.customer_postal),
                    search.TextField(name="cust_address_full", value=app_entry.customer_address + " " + app_entry.customer_city + ", " + app_entry.customer_state + " " + app_entry.customer_postal)
                ]
            )
        )
        if len(docs_to_put) == 50:
            lst.append(list(docs_to_put))
            docs_to_put = []

    for item in lst:
        index.put(item)
