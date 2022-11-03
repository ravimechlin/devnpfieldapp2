def lb_patch(self):
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    from google.appengine.api import taskqueue
    
    stats = LeaderBoardStat.query(
            LeaderBoardStat.metric_key == "packets_submitted"
        )
    for stat in stats:
        app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == stat.field_app_identifier)
        if not app_entry is None:
            rep = FieldApplicationUser.first(FieldApplicationUser.rep_id == app_entry.rep_id)
            if not rep is None:
                stat.rep_id = rep.rep_id
                stat.put()
