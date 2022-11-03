@staticmethod
def get_html_path(name):
    path = os.path.join(os.path.dirname(__file__), '..', name)
    return path
