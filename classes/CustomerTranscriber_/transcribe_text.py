@staticmethod
def transcribe_text(app_entry_identifier=None, user_identifier=None, txt=None, blob_count=0):
    """Add a message by txt string."""
    if txt is None:
        logging.error("No text was given to post a message")
        return None
    content = {"txt": [txt]}
    return CustomerTranscriber.transcribe_object(app_entry_identifier, user_identifier, content, blob_count)


