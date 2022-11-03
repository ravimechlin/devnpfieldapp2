@staticmethod
def transcribe_object(app_entry_identifier=None, user_identifier=None, content=None, blob_count=0, n_key="n/a"):
    """Add a message by txt string."""
    if app_entry_identifier is None:
        logging.error("A FieldApplicationEntry identifier is required to post a message")
        return None
    if user_identifier is None:
        logging.error("A user identifier is required to post a message")
        return None
    if content is None:
        logging.error("No message object given to post a message")
        return None

    note_id = Helpers.guid()
    try:
        note = CustomerNote(
            identifier=note_id,
            field_app_identifier=app_entry_identifier,
            inserted_pacific=Helpers.pacific_now(),
            inserted_utc=datetime.now(),
            author=user_identifier,
            perms="public",
            content=json.dumps(content),
            blob_count=blob_count,
            note_key=n_key,
            read=False
        )
        designee = note.get_designee()
        note.read = ((designee == note.author) or (designee is None))
        note.put()

        if (not note.read) and (not designee is None):
            f = GCSLockedFile("/ApplicationSettings/UserSettings/Notifications/" + designee + ".json")
            content = f.read()
            if not content is None:
                settings = json.loads(content)
                if "new_customer_note" in settings.keys():
                    if settings["new_customer_note"]["sms"] == True:
                        try:
                            app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == app_entry_identifier)
                            rep = FieldApplicationUser.first(FieldApplicationUser.identifier == designee)
                            if (not app_entry is None) and (not designee is None):
                                msg = "a new note for one of your customers (" + app_entry.customer_first_name.strip() + " " + app_entry.customer_last_name.strip() + ") got recorded in the field app."
                                #Helpers.send_sms(rep.rep_phone, msg)
                        except:
                            logging.error("SMS failed")
                    if settings["new_customer_note"]["email"] == True:
                        try:
                            msg = "msg"
                            #msg2 = rep.first_name.strip() + " " + rep.last_name.strip() + ",\n\nA new note for " + app_entry.customer_first_name.strip() + " " + app_entry.customer_last_name.strip() + " was recorded:\n\n\"" + note.content + "\""
                            #Helpers.send_email(rep.rep_email, "New Customer Note!", msg2)
                        except:
                            logging.error("Customer note notification failed")

    except:
        exctype, value = sys.exc_info()[:2]
        logging.error("note put error({0}): {1} while putting jsonObject".format(exctype, value))
        note_id = None

    return note_id

