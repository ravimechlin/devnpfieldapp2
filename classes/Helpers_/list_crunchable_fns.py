@staticmethod
def list_crunchable_fns():
    import os.path
    path = os.path.dirname(__file__) + "/Helpers_/_crunch.py"
    logging.info(path)
    f = open(os.path.dirname(__file__) + '/Helpers_/_crunch.py')
    content = f.read()
    words = content.split(" ")
    fns = []
    for word in words:        
        if "fx_" in word.replace("\"", "").replace(":", ""):
            candidate = word.replace("\"", "").replace(":", "").replace("Helpers.crunch", "").replace("(", "").replace(")", "").replace(",", "").replace("[", "").replace("]", "").strip()
            if not candidate in fns:
                fns.append(candidate)
    
    return fns

