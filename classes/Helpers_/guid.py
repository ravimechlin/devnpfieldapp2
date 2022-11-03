@staticmethod
def guid():
    return hashlib.sha512(str(uuid4())).hexdigest()

