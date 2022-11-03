def ca_audit(self):
    counties = ["San Diego County", "Riverside County", "Orange County", "San Bernadino County", "Los Angeles County", "Kern County", "Ventura County"]
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.customer_county.IN(counties))
    lst = []
    for app_entry in app_entries:
        lst.append(app_entry.customer_address.upper() + " " + app_entry.customer_postal)

    f = GCSLockedFile("/ca_audit.json")
    f.write(json.dumps(lst), "application/json")
