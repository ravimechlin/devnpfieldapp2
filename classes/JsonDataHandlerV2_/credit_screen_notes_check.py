def credit_screen_notes_check(self):
    self.response.content_type = "application/json"
    ret_json = {"has_notes": False}
    note = CustomerNote.first(
        ndb.AND(
            CustomerNote.note_key == "credit_screen_notes",
            CustomerNote.field_app_identifier == self.request.get("identifier")
        )
    )
    if not note is None:
        ret_json["has_notes"] = True

    self.response.out.write(json.dumps(ret_json))
