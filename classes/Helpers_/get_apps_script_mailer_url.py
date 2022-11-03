@staticmethod
def get_apps_script_mailer_url():
    import time
    import random

    now = int(time.time())
    now_str = str(now)
    last_digit = now_str[-1]

    random.seed(now)

    urls = ["https://script.google.com/macros/s/AKfycbxz3GitrSrOgRu56fYKDkAwWoYb6uVMjvfYya7cRUvMPQP4w5o2/exec", "https://script.google.com/macros/s/AKfycbxF-03Kkv2FD3PyMTLlkrc7yVLnGhEqRUAHMu7oCiBVbJf3FCW0/exec", "https://script.google.com/macros/s/AKfycbzJ1g4t8nJofkoUMFsyHjmtkcbPA7FQASevIhF865lrslM9k7yI/exec"]
    
    idx = random.randint(0, len(urls) - 1)
    
    #idx = None
    #if last_digit < 3:
    #    idx = 0
    #elif last_digit < 7:
    #    idx = 1
    #else:
    #    idx = 2

    #if len(urls) < 3:
    #    idx = 0

    return urls[idx]

