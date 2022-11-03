def post(self):
    data = json.loads(self.request.get("data"))
    cell_values = data["cell_values"]
    items_to_save = []
    for key in cell_values.keys():
        cell_key = key

        passed_entity_identifiers = ["-1"]
        count = 0

        entity_identifier_entity_type_dict = {}
        entity_identifier_cell_key_cell_val_dict = {}
        while count < len(cell_values[key]):
            passed_entity_identifiers.append(cell_values[key][count]["entity_identifier"])
            entity_identifier_entity_type_dict[cell_values[key][count]["entity_identifier"]] = cell_values[key][count]["entity_identifier_type"]
            entity_identifier_cell_key_cell_val_dict[cell_values[key][count]["entity_identifier"] + "_" + key] = cell_values[key][count]["cell_value"]
            count += 1

        sheet_items = SheetDataItem.query(
            ndb.AND
            (
                SheetDataItem.entity_identifier.IN(passed_entity_identifiers),
                SheetDataItem.sheet_key == self.request.get("sheet_key"),
                SheetDataItem.cell_key == cell_key
            )
        )

        existing_entity_identifiers = ["-1"]
        for sheet_item in sheet_items:
            existing_entity_identifiers.append(sheet_item.entity_identifier)

        missing_entity_identifiers = ["-1"]

        for item in cell_values[key]:
            try:
                idx = existing_entity_identifiers.index(item["entity_identifier"])
            except:
                missing_entity_identifiers.append(item["entity_identifier"])

        existing_sheet_items = SheetDataItem.query(
            ndb.AND
            (
                SheetDataItem.entity_identifier.IN(existing_entity_identifiers),
                SheetDataItem.sheet_key == self.request.get("sheet_key"),
                SheetDataItem.cell_key == cell_key
            )
        )

        for existing_sheet_item in existing_sheet_items:
            existing_sheet_item.cell_value = entity_identifier_cell_key_cell_val_dict[existing_sheet_item.entity_identifier + "_" + cell_key]
            items_to_save.append(existing_sheet_item)

        for missing_item in missing_entity_identifiers:
            if missing_item in entity_identifier_entity_type_dict.keys():
                sheet_data_item = SheetDataItem(
                    identifier=Helpers.guid(),
                    entity_identifier=missing_item,
                    entity_identifier_type=entity_identifier_entity_type_dict[missing_item],
                    cell_key=key,
                    cell_value=entity_identifier_cell_key_cell_val_dict[missing_item + "_" + cell_key],
                    sheet_key=self.request.get("sheet_key")
                )
                items_to_save.append(sheet_data_item)


    if len(items_to_save) == 1:
        items_to_save[0].put()
    elif len(items_to_save) > 1:
        ndb.put_multi(items_to_save)
    else:
        items_to_save = []

    self.response.out.write(" ")



