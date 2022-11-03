def get(self):
    template_values = {}
    offices = []
    markets = []
    office_locations = OfficeLocation.query(
        ndb.AND
        (
            OfficeLocation.is_parent == False,
            OfficeLocation.active == True
        )
    )
    parent_tally_dict = {}
    for office_location in office_locations:
        office = {}
        office["identifier"] = office_location.identifier
        office["name"] = office_location.name
        office["parent"] = office_location.parent_identifier
        offices.append(office)
        if not (office["parent"] in parent_tally_dict.keys()):
            parent_tally_dict[office["parent"]] = 0
        parent_tally_dict[office["parent"]] += 1

    markets = []
    market_items = OfficeLocation.query(OfficeLocation.is_parent == True)
    for market in market_items:
        m = {}
        m["identifier"] = market.identifier
        m["name"] = market.name
        if m["identifier"] in parent_tally_dict.keys():
            if parent_tally_dict[m["identifier"]] > 0:
                markets.append(m)

    template_values["offices"] = json.dumps(offices)
    template_values["markets"] = json.dumps(markets)
    path = Helpers.get_html_path('registration.html')
    self.response.out.write(template.render(path, template_values))
