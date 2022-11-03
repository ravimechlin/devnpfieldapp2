@staticmethod
def mail(to, subject, message, attachments=None):
    from google.appengine.api import mail
    from io import StringIO
    msg = mail.EmailMessage()
    msg.sender = "noreply@newpower.net"
    msg.to = to
    msg.subject = subject
    msg.body = message
    msg.bcc = "archive@newpower.net"
    msg.html = message.replace("\r\n", "<br />").replace("\n", "<br />")
    if not attachments is None:
        buffs = []
        gcs_files = []
        attaches = []
        for attachment in attachments:
            gcs_files.append(GCSLockedFile(attachment["gcs_path"]))
            attach = (attachment["name"],  gcs_files[len(gcs_files) - 1].read())
            attaches.append(attach)
        msg.attachments = attaches
    msg.send()

