@staticmethod
def kill_current_cpf_session():
    today = datetime.now().date()
    keyy = "cpf_php_session_id_" + str(today.month) + "_" + str(today.day) + "_" + str(today.year)
    memcache.delete(keyy)

