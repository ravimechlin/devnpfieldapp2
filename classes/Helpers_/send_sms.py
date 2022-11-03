@staticmethod
def send_sms(recipient, message, origin=None, attachment=None):
    from google.appengine.api import urlfetch
    import base64

    account_sid = "AC62604e9a588ac09c2da2e019573ea9ed"
    auth_token = "b920f0c1393cadb2fa7b0b51b540a102"

    form_fields = {}
    form_fields["Body"] = message
    form_fields["From"] = "+19512526641"
    if not origin is None:
        form_fields["From"] = origin

    form_fields["To"] = "+1" + recipient

    req_headers = {}
    req_headers["Authorization"] = "Basic " + base64.b64encode(account_sid + ":" + auth_token)

    

    urlfetch.fetch(
        url="https://api.twilio.com/2010-04-01/Accounts/" + account_sid + "/Messages.json",
        method=urlfetch.POST,
        payload=urllib.urlencode(form_fields),
        deadline=30,
        headers = req_headers
    )
    return


    #rv = None
    #if recipient == "5555555555":
    #    return

    #from twilio import twiml
    #from twilio.rest import TwilioRestClient

    #account_sid = "AC62604e9a588ac09c2da2e019573ea9ed"
    #auth_token = "b920f0c1393cadb2fa7b0b51b540a102"
    #client = TwilioRestClient(account_sid, auth_token)
    # replace "to" and "from_" with real numbers
    #rv = None
    #fromm = "+19512526641"
    #if not origin is None:
    #    fromm = origin
    #if 5 == 5:
    #    if attachment is None:
    #        rv = client.messages.create(to="+1" + recipient,
    #                                    from_=fromm,
    #                                    body=message)
    #    else:
    #        rv = client.messages.create(to="+1" + recipient,
    #                                    from_=fromm,
    #                                    body=message,
    #                                    media_url=attachment)
    #else:
    #    rv = rv
    #return rv

