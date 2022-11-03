def notify_rep_for_missing_docs(self):
    identifier = self.request.get("identifier")
    app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == identifier)
    if not app_entry is None:
        rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
        if not rep is None:
            msg = "Hey " + rep.first_name.strip().title() + ", the PM says your customer (" + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title() + ") is missing the following docs: " + self.request.get("notes") + ". Please get these docs and email to newpower@newpower.net. If we don't receive these docs in 5 days the customer will be marked as a cancel."
            Helpers.send_sms(rep.rep_phone, msg)

            missing_docs_note_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "missing_docs_details_" + identifier)
            if missing_docs_note_kv is None:
                missing_docs_note_kv = KeyValueStoreItem(
                    identifier=Helpers.guid(),
                    keyy="missing_docs_details_" + identifier,
                    expiration=datetime(1970, 1, 1)
                )
            missing_docs_note_kv.val = self.request.get("notes")
            missing_docs_note_kv.put()
