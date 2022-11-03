def phix_offsets(self):
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    
    tyme = int(time.time() * 1000)
    tyme -= (1000 * 60 * 60 * 24 * 180)
    app_entries = FieldApplicationEntry.query(FieldApplicationEntry.insert_time > tyme)
    app_entry_identifier_total_kwhs_dict = {}
    ids_to_query = ["-1"]
    for app_entry in app_entries:
        app_entry_identifier_total_kwhs_dict[app_entry.identifier] = app_entry.total_kwhs
        ids_to_query.append(app_entry.identifier)
    
    proposals = CustomerProposalInfo.query(CustomerProposalInfo.field_app_identifier.IN(ids_to_query))
    info = None
    keyss = None
    tkwhs = None
    y1prod = None
    nums = ["0", "1", "2","3","4", "5", "6", "7", "8","9", "."]
    saved_cnt = 0
    for proposal in proposals:
        info = json.loads(proposal.info)
        keyss = info.keys()
        if "offset" in keyss and "year_one_production" in keyss:
            tkwhs = float(app_entry_identifier_total_kwhs_dict[proposal.field_app_identifier])
            if(tkwhs > float(0)):

                y1prod = ""                
                for ch in info["year_one_production"]:
                    if ch in nums:
                        y1prod += ch

                y1prod = float(y1prod)                
                percentage = y1prod / tkwhs
                percentage *= float(100)
                if percentage > float(100):
                    percentage = float(100)
                percentage = int(percentage)
                info["offset"] = str(percentage) + "%"
                proposal.info = json.dumps(info)
                proposal.put()
                saved_cnt += 1

    Helpers.send_email("rnirnber@gmail.com", "results", str(saved_cnt))
