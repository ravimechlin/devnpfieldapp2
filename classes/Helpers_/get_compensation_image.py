@staticmethod
def get_compensation_image(server_name, user_type,user_primary_state):

	path = "https://" + server_name + "/bootstrap/images/comp/" + user_primary_state + "/" + user_type + ".pdf"

	return path



