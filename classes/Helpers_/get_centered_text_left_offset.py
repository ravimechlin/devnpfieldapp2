@staticmethod
def get_centered_text_left_offset(fnt, txt, box_width):
    w, h = fnt.getsize(txt)
    l_off = float(box_width) - float(w)
    l_off /= float(2)
    l_off = int(l_off)
    if l_off < 0:
        l_off = 0

    return l_off

