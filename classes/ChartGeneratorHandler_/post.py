def post(self):
    from datetime import datetime

    csv_content = self.request.POST.multi['csv'].file.read()
    template_values = {"csv": csv_content}
    f = GCSLockedFile("/ApplicationSettings/soiling_levels.json")
    data = json.loads(f.read())
    f.unlock()
    template_values["soiling_level"] = "Moderate"
    template_values["cleaning_recommended"] = "Yes"
    
    identifier = self.request.get("identifier")
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == identifier)
    if not app_entry is None:
        readers = SolarReader.query(SolarReader.field_app_identifier == app_entry.identifier)
        for reader in readers:
            reader.rep_ownership = self.request.get("rep_identifier")
            
            flag_value =  str(self.request.get(("stay_deployed")))
            if not flag_value == "1":
                reader.deployment_dt = datetime(1970, 1, 1)
            reader.retrieval_dt = Helpers.pacific_now()
            reader.put()

        existing_stat = LeaderBoardStat.first(
            ndb.AND(
                LeaderBoardStat.field_app_identifier == identifier,
                LeaderBoardStat.metric_key == "data_logger_retrieved"
            )
        )
        if existing_stat is None:
            new_stat = LeaderBoardStat(
                identifier=Helpers.guid(),
                rep_id=app_entry.rep_id,
                dt=Helpers.pacific_now(),
                metric_key="data_logger_retrieved",
                office_identifier=app_entry.office_identifier,
                field_app_identifier=app_entry.identifier,
                in_bounds=True,
                pin_identifier="-1"
            )
            new_stat.put()

        for key in data.keys():
            items = data[key]
            if app_entry.customer_postal in items:
                template_values["soiling_level"] = key

        if template_values["soiling_level"] == "little_to_none":
            template_values["cleaning_recommended"] = "No"

        new_str = ""
        key_values = template_values["soiling_level"].split("_")
        for key in key_values:
            word = key.title()
            new_str += word
            new_str += " "
        new_str = new_str.strip()
        template_values["soiling_level"] = new_str


        path = Helpers.get_html_path('solar_reader_chart_gen.html')
        self.response.out.write(template.render(path, template_values))
