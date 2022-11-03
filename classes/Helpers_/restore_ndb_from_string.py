@staticmethod
def restore_ndb_property_from_string(entity, key, val):
    t = val["type"]
    v = val["value"]
    t_v = None
    if t == "ndb.StringProperty":
        t_v = v

    if t == "ndb.TextProperty":
        t_v = v

    if t == "ndb.BooleanProperty":
        t_v = (v == "True")

    if t == "ndb.FloatProperty":
        t_v = float(v)

    if t == "<type 'unicode'>":
        t_v = v

    if t == "<type 'datetime.date'>":
        d_items = v.split("-")
        t_v = date(int(d_items[0]), int(d_items[1]), int(d_items[2]))

    if t == "<type 'datetime.datetime'>":
        deserialized_dt = Helpers.string_to_datetime(v)

        if not (deserialized_dt is None):
            t_v = deserialized_dt
        else:
            # will cause an error when the entity gets put !!!!
            t_v = -25


    if t == "ndb.DateProperty":
       d_items = v.split("-")
       t_v = date(int(d_items[0]), int(d_items[1]), int(d_items[2]))

    if t == "ndb.DateTimeProperty":
        #datetime(1970, 1, 1, 0, 0)
        t_v = eval(v)

    if t == "<type 'int'>":
        t_v = int(v)

    if t == "<type 'long'>":
        t_v = long(v)

    if t == "<type 'bool'>":
        t_v = (v == 'True')

    if t == "<type 'float'>":
        t_v = float(v)

    if t == "ndb.IntegerProperty":
        t_v = int(v)

    if t == "<type 'list'>":
        try:
            t_v = eval(v)
        except:
            t_v = eval(v.replace("datetime.datetime", "datetime"))

    if "ndb.StructuredProperty<" in t:
        entity2 = eval(t.replace("ndb.StructuredProperty<", "").replace(">", "") + "()")
        for att in v.keys():
            Helpers.restore_ndb_property_from_string(entity2, att, v[att])

        t_v = entity2

    if not t_v is None:
        setattr(entity, key, t_v)
    else:
        if key == "notes":
            setattr(entity, key, "")
        logging.info("No typed value...")
        logging.info(t)

