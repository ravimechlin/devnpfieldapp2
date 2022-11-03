@staticmethod
def hash_pass(plain_text):
    in_str = Salt.default() + plain_text + Salt.default()
    return hashlib.sha512(in_str).hexdigest()

