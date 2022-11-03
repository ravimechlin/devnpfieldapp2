def percentage_of_pins_changed(self):
    ret_json = {}
    self.response.content_type = "application/json"
    pin_tally = 0
    changed_pins_tally = 0

    pins = PinPoint.query(PinPoint.quadrant_identifier == self.request.get("identifier"))
    for pin in pins:
        pin_tally += 1
        changed_pins_tally += int((not pin.status == 2) and (not pin.status == 7))

    ret_json["percentage"] = str(int(float((float(changed_pins_tally) / float(pin_tally)) * float(100))))
    ret_json["tally"] = pin_tally
    ret_json["changed_tally"] = changed_pins_tally
    self.response.out.write(json.dumps(ret_json))
