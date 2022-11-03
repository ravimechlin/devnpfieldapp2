@staticmethod
def constanticize(wrd):
    wrd = wrd.replace("a", "").replace("A", "")
    wrd = wrd.replace("e", "").replace("E", "")
    wrd = wrd.replace("i", "").replace("I", "")
    wrd = wrd.replace("o", "").replace("O", "")
    wrd = wrd.replace("u", "").replace("U", "")
    wrd = wrd.replace("y", "").replace("Y", "")
    wrd = wrd.replace("_", "")
    return wrd.upper()

