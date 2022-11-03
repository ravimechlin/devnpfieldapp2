def update_credit_screen_notes(self):
    note = CustomerNote.first(
        ndb.AND(
            CustomerNote.note_key == "credit_screen_notes",
            CustomerNote.field_app_identifier == self.request.get("identifier")
        )
    )
    if not note is None:
        content = json.loads(note.content)
        content["txt"][0] = self.request.get("txt")
        note.content = json.dumps(content)
        note.put()
