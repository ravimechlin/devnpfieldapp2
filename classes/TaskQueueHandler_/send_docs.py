def send_docs(self):
    
    from PyPDF2 import PdfFileWriter,PdfFileReader
    from io import BytesIO
    import StringIO
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    from google.appengine.api import taskqueue
    
    retryParameters = gcs.RetryParams(initial_delay=0.2,
                                            max_delay=5.0,
                                            backoff_factor=2,
                                            max_retry_period=15,
                                            urlfetch_timeout=30)

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)

    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    idxs = json.loads(self.request.get("idxs"))
    pdfs = []
    pdf_bytes = []
    cnt = 0
    for idx in idxs:

        filename_a = bucket + '/TempDocs/' + self.request.get("token") + "_" + str(idx) + ".pdf"
        file_a = gcs.open(filename_a, 'r', retry_params=retryParameters)
        pdf_bytes.append(BytesIO(file_a.read()))
        pdfs.append(PdfFileReader(pdf_bytes[cnt]))
        file_a.close()
        gcs.delete(filename_a)
        cnt += 1

    out_pdf = PdfFileWriter()
    for pdf in pdfs:
        pdf_page_cnt = 0
        while pdf_page_cnt < pdf.getNumPages():
            out_pdf.addPage(pdf.getPage(pdf_page_cnt))
            pdf_page_cnt += 1

    filename_b = bucket + "/TempDocs/" + self.request.get("token") + ".pdf"
    file_b = gcs.open(filename_b, 'w', content_type="application/pdf", options={'x-goog-meta-foo': 'foo',
                                                                                'x-goog-meta-bar': 'bar',
                                                                                'x-goog-acl': 'public-read'},
                                                                        retry_params=write_retry_params)
    buff = StringIO.StringIO()
    out_pdf.write(buff)
    buff.seek(2)
    file_b.write(buff.getvalue())
    file_b.close()
    buff.close()

    for bytes in pdf_bytes:
        bytes.close()

    attachment_data = {}
    attachment_data["data"] = ["https://storage.googleapis.com" + bucket + "/TempDocs/" + self.request.get("token") + ".pdf"]
    attachment_data["content_types"] = ["application/pdf"]
    attachment_data["filenames"] = ["signing_docs_for_" + self.request.get("customer_name") + ".pdf"]
    Helpers.send_email(self.request.get("rep_email"), "Docs for " + self.request.get("customer_name").replace("_", " "), "Attached are your docs...\n\nThanks!", attachment_data)
