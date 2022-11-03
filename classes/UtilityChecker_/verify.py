@staticmethod
def verify(provider_code, utility_no, postal):
    return eval("UtilityChecker._verify_" + provider_code + "(" + utility_no + ", " + postal + ")")

