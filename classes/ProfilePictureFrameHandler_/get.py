def get(self, identifier, width, height):
    import StringIO
    from PIL import Image
    from io import BytesIO

    gcs_file = GCSLockedFile("/Images/ProfilePictures/Full/" + identifier + ".jpg")
    img_data = gcs_file.read()
    if not img_data is None:
        bytez = BytesIO(img_data)
        buff = StringIO.StringIO()
        img = Image.open(bytez)
        img = img.resize((int(width), int(height)), Image.ANTIALIAS)
        img.save(buff, format="JPEG")
        template_dict = {}
        template_dict["width"] = width
        template_dict["height"] = height
        template_dict["b64"] = base64.b64encode(buff.getvalue())
        bytez.close()
        buff.close()
        path = Helpers.get_html_path('img.html')
        self.response.out.write(template.render(path, template_dict))
