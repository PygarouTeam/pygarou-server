class User:
	def __init__(self, id, socket, ip, username="unknown"):
		self.id = id
		self.socket = socket
		self.ip = ip

		if username == "unknown":
			self.username = "unknown_" + str(self.id)

	def get_id(self):
		return self.id

	def get_socket(self):
		return self.socket

	def get_ip(self):
		return self.ip

	def get_username(self):
		return self.username

	def set_username(self, username):
		self.username = username
