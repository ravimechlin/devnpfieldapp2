@staticmethod
def decrypt(ciphertext):
      import base64
      return base64.b64decode(ciphertext)

