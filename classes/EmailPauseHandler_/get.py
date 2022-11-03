def get(self, hours):
    hourss = int(hours)
    self.session = get_current_session()
    email_address = self.session["user_email"]

    exp = Helpers.pacific_now() + timedelta(hours=hourss)

    existing_kv = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "pause_emails_" + email_address)
    if existing_kv is None:
        email_kv = KeyValueStoreItem(
            identifier=Helpers.guid(),
            keyy="pause_emails_" + email_address,
            val="1",
            expiration=exp
        )
        email_kv.put()

