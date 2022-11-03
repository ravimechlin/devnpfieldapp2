def get_rep_notes_for_lead(self):
    self.response.content_type = "application/json"
    ret_json = {"notes": "No notes were recorded."}
    note = CustomerNote.first(
        ndb.AND(
            CustomerNote.field_app_identifier == self.request.get("identifier"),
            CustomerNote.note_key == "rep_lead_notes"
        )
    )
    if not note is None:
        ret_json["notes"] = json.loads(note.content)["txt"][0]

    self.response.out.write(json.dumps(ret_json))
