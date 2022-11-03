@staticmethod
def images_equal(path1, path2):
    from PIL import Image, ImageChops
    from io import BytesIO
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name
    retryParameters = gcs.RetryParams(initial_delay=0.2,
                                                max_delay=5.0,
                                                backoff_factor=2,
                                                max_retry_period=15,
                                                urlfetch_timeout=30)

    path1 = bucket + path1
    path2 = bucket + path2

    f1 = gcs.open(path1, 'r', retry_params=retryParameters)
    f2 = gcs.open(path2, 'r', retry_params=retryParameters)
    img_bytes1 = BytesIO(f1.read())
    img_bytes2 = BytesIO(f2.read())
    im1 = Image.open(img_bytes1)
    im2 = Image.open(img_bytes2)

    diff = ImageChops.difference(im1, im2).getbbox()

    f1.close()
    f2.close()
    img_bytes1.close()
    img_bytes2.close()

    return (diff is None)

