@staticmethod
def grant_sales_rabbit_access(email,first_name,last_name,form_office, office_obj):
    sr_office_id = str(office_obj.sales_rabbit_id)
    sr_area_id = str(office_obj.sales_rabbit_area_id)
    user_payload = {
            "email" : email,
            "first": first_name,
            "last": last_name,
            "area": sr_area_id,
            "office" : sr_office_id
    }
    user_payload = urllib.urlencode(user_payload)

    resp2 = urlfetch.fetch(url="https://script.google.com/macros/s/AKfycbxiyWcucD6Mk26Pg_ixtr6t4ooNEyT0aw7xdIFh3Fw44xSkv68/exec",
                deadline=30,
                headers=
                {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36",
                },
                payload=user_payload,
                method=urlfetch.POST,
                follow_redirects=False
        )



    return -1


