def seed_transactions_search(self):
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    from google.appengine.api import app_identity

    idx = search.Index(name="v2_transactions")
    transactions = MonetaryTransactionV2.query(
        ndb.AND
        (
            MonetaryTransactionV2.approved == True,
            MonetaryTransactionV2.denied == False
        )
    )
    for t in transactions:
        doc = search.Document(
            fields=[
                search.TextField(name="description", value=t.description),
                search.TextField(name="identifier", value=t.identifier),
            ]
        )
        idx.put(doc)
