def get_admin_notes_and_checklist_for_lead(self):
    self.response.content_type = "application/json"
    ret_json = {"admin_notes": "No notes were recorded", "admin_checklist": []}
    note = CustomerNote.first(
        ndb.AND(
            CustomerNote.note_key == "admin_lead_notes",
            CustomerNote.field_app_identifier == self.request.get("identifier")
        )
    )
    if not note is None:
        ret_json["admin_notes"] = json.loads(note.content)["txt"][0]

    checklist = Helpers.read_setting("lead_checklist")
    checklist_name_idx_dict = {}
    for item in checklist:
        checklist_name_idx_dict[item] = len(checklist_name_idx_dict.keys())

    for item in checklist:
        ret_json["admin_checklist"].append({"name": item, "checked": False, "date": "1970-01-01"})

    checklist_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "lead_checklist_for_" + self.request.get("identifier"))
    if not checklist_kv is None:
        value = json.loads(checklist_kv.val)
        for item in value.keys():
            cnt = 0
            for item2 in ret_json["admin_checklist"]:
                if item2["name"] == item:
                    ret_json["admin_checklist"][checklist_name_idx_dict[item2["name"]]] = value[item]
                cnt += 1

    ret_json["notes"] = ret_json["admin_notes"]
    self.response.out.write(json.dumps(ret_json))
