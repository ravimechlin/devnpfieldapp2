@staticmethod
def read_email_template(template_name):
    resp = urlfetch.fetch(url="https://script.google.com/macros/s/AKfycbyhJiijpo3IVyOZ7jGVX-HK45cgZa7OS9Br7nm9zgiqXUAp1g7k/exec?filename=" + template_name,
        deadline=30,
        method=urlfetch.GET)
    return resp.content
