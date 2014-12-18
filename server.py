import threading
import socket
import yaml

from User import User


users = dict()
users_db = yaml.load(open("data\\users.yaml", 'rw'))


def main(ip="127.0.0.1", port=2778):
	start(ip, port)


def start(ip, port):
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((ip, port))

	id = -1
	while True:
		id += 1
		print("waiting for new client...")

		server_socket.listen(0)

		client_socket, client_info = server_socket.accept()

		users[id] = User(id, client_socket, client_info[0])

		sessionThread = threading.Thread(target=auth, args=(id,))
		sessionThread.start()

	server_socket.close()


def auth(id):
	this_socket = users[id].get_socket()
	print(users[id].get_ip(), "is now connected to you")

	try:
		# Authentificating
		data = receive(this_socket)
		assert data[0] == 0x1, "0x1 was expected"
		send(this_socket, 0x2)

		data = receive(this_socket)
		assert data[0] == 0x3, "0x3 was expected"
		assert data[1].isalpha(), "the username must contain only alpha characters"
		assert data[1] in users_db['users'], "the username is not registered"
		users[id].set_username(data[1])
		send(this_socket, 0x2)

		data = receive(this_socket)
		assert data[0] == 0x5, "0x5 was expected"
		assert data[1] == users_db[users[id].get_username()]['password'], "wrong password"
		send(this_socket, 0x2)

		session(id)

	except AssertionError as ex:
		print("AssertionError:", ex)
	except Exception as ex:
		print("Exception:", ex)


def session(id):
	this_socket = users[id].get_socket()
	print(users[id].get_ip(), "is now in session")

	send_toall((0x7, users[id].get_username()))


def send(user_id, data):
	if type(data) != tuple:
		data = (data,)

	users[user_id].get_socket().send((yaml.safe_dump(data) + "\n").encode())


def send_toall(data, blackids):  # TODO: Take in account dead socket
	if type(data) != tuple:
		data = (data,)
	if type(blackids) != tuple:
		blackids = (blackids,)

	for item in users:
		if item.get_id() in blackids:
			continue

		item.get_socket().send((yaml.safe_dump(data) + "\n").encode())


def receive(client_socket):
	return yaml.load(str(client_socket.recv(1024), encoding='utf-8'))

if __name__ == "__main__":
	main()


"""
Server Local Error Protocol v*:

"""

"""
Auth Protocol v0.1:
	0x1 - Client is ready to auth
	0x2 - Server is ready to *

	0x3 <username> - Client username
	0x5 <password> - Client password

	0x4 - (server) Unregistered username
	0x6 - (server) Wrong password

	0x7 <username> - (server) new user connected
	"""
