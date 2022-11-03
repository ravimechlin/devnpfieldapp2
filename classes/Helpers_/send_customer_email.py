@staticmethod
def send_customer_email(html, subject, recipient, note_content, field_app_identifier):
    import time
    import random

    now = int(time.time())
    now_str = str(now)
    last_digit = now_str[-1]

    random.seed(now)

    urls = ["https://script.google.com/macros/s/AKfycbw1hOk77emB7qSo-a2apP7aU3uD4lCjHsgEQU2ofYRtcZmyfT3z/exec", "https://script.google.com/macros/s/AKfycbwZvKFyVXOQ_sEqVJNIUPFgb-qLIW6h6a2Z5UCQOYU3AwaqsAFx/exec", "https://script.google.com/macros/s/AKfycbzHwObRn6RWgrWJsmMJKdjpxDIsKlOi8TGQnMPpuUz9aiKv1Qs/exec"]

    idx = random.randint(0, len(urls) - 1)
    
    
    you_r_l = urls[idx]
    form_fields = {"to": recipient, "subject": subject, "html": html}
    form_data = urllib.urlencode(form_fields)

    resp = urlfetch.fetch(
                            url=you_r_l,
                            payload=form_data,
                            deadline=45,
                            method=urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    content_dict = {}
    content_dict["txt"] = [note_content]
    CustomerTranscriber.transcribe_object(field_app_identifier,
                                                    "-1",
                                                    content_dict,
                                                    0,
                                                    "cust_comm")
