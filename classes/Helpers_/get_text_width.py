@staticmethod
def get_text_width(fnt, txt):
    w, h = fnt.getsize(txt)
    return int(w)


