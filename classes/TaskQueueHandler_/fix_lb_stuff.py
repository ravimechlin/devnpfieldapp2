def fix_lb_stuff(self):
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    from google.appengine.api import taskqueue
    
    offices = OfficeLocation.query()
    office_identifier_name_dict = {}
    for office in offices:
        office_identifier_name_dict[office.identifier] = office.name
    
    stats = LeaderBoardStat.query().order(-LeaderBoardStat.recorded_dt)
