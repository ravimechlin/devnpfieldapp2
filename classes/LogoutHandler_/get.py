def get(self):
    self.session = get_current_session()
    self.session.terminate()
    self.response.out.write("<html><head><title>Logging Out</title><script type='text/javascript'>window.location.href = './';</script></head><body></body></html>")
