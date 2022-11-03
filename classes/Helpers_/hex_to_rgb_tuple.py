@staticmethod
def hex_to_rgb_tuple(hex):
    if hex[0] == "#":
        hex = hex[1:]
    return (
        int(hex[0:2], 16),
        int(hex[2:4], 16),
        int(hex[4:6], 16)
    )

