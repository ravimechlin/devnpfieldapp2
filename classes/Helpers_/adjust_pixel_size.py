@staticmethod
def adjust_pixel_size(size, fromm, to):
    num = ((float(size) * float(to)) / float(fromm))
    num = round(num, 0)
    return int(num)


