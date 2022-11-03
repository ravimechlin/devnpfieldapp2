def reassign_pins(self):
    now = Helpers.pacific_now()
    pins = PinPoint.query(PinPoint.quadrant_identifier == self.request.get("identifier"))
    pins_to_save = []
    for pin in pins:
        pin.created = Helpers.pacific_now()
        pin.modified = Helpers.pacific_now()
        pin.rep_identifier == self.request.get("new_rep_identifier")
        pin.status = 2
        pins_to_save.append(pin)

    if len(pins_to_save) == 1:
        pins_to_save[0].put()
    elif len(pins_to_save) > 1:
        ndb.put_multi(pins_to_save)
