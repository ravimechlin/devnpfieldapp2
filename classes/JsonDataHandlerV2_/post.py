def post(self):
    fn = getattr(self, self.request.get("fn"))
    fn()
