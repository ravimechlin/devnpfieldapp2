@staticmethod
def shorten_url(you_rl):    
    return you_rl
    import urllib
    resp = urlfetch.fetch(
        url="https://to.ly/api.php?json=1&longurl=" + urllib.quote(you_rl),
        method=urlfetch.GET,
        deadline=30,
        follow_redirects=True
    )
    return json.loads(resp.content[1:len(resp.content) - 1])["shorturl"]
