import threading
import pickle
import os
import ipaddress
from pprint import pprint
import socket
from queue import Queue
import json

DOCKERS_DB_PATH = "db/dockers"
HOST = "127.0.0.1"
PORT = 4000
MSG_SIZE = 1024
SOCK_TIMEOUT = 120
NO_NEW_CONFIG = "no new config"

class Connection(threading.Thread):
	def __init__(self, server, logger, conn, addr):
		threading.Thread.__init__(self)
		self.server = server
		self.logger = logger
		self.conn = conn
		self.addr = addr

	def run(self):
		self.conn.settimeout(SOCK_TIMEOUT)

		while True:
			try:
				msg = self.conn.recv(MSG_SIZE)

				if not msg:
					raise Exception("conn closed")

				self.server.enqueue(self.addr, msg)

			except Exception as e:
				self.logger.log(f"Conn {self.addr} died.")
				self.server.rem_conn(self.addr)
				break

class Listener(threading.Thread):
	def __init__(self, server, logger):
		threading.Thread.__init__(self)
		self.server = server
		self.logger = logger

	def run(self):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((HOST, PORT))

			while True:
				s.listen()
				conn, addr = s.accept()
				self.logger.log(f"addr {addr} connected.")
				self.start_conn_thread(conn, addr)
				self.server.add_conn(conn, addr)

	def start_conn_thread(self, conn, addr):
		connThread = Connection(self.server, self.logger, conn, addr)
		connThread.setDaemon(True)
		connThread.start()

class Server(threading.Thread):
	def __init__(self, args, logger, reporter, configuration_manager):
		threading.Thread.__init__(self)
		self.args = args
		self.logger = logger
		self.reporter = reporter
		self.configuration_manager = configuration_manager
		self.queue = Queue()
		self.conns = {}

		if not self.load_dockers_db():
			self.dockers = {}
			self.save_dockers_db()

	def enqueue(self, addr, msg):
		#print (msg)
		self.queue.put((addr, msg))

	def add_conn(self, conn, addr):
		self.conns[addr] = conn
		self.logger.log(f"Server has {len(self.conns)} connections up.")

	def rem_conn(self, addr):
		if addr in self.conns.keys():
			del self.conns[addr]

		self.logger.log(f"Server has {len(self.conns)} connections up.")

	def run(self):
		self.start_listener_thread()

		while True:
			addr, msg = self.queue.get()
			self.reporter.enqueue(addr, msg)

	def start_listener_thread(self):
		self.listener = Listener(self, self.logger)
		self.listener.setDaemon(True)
		self.listener.start()

	def load_dockers_db(self):
		if os.path.isfile(DOCKERS_DB_PATH):
			with open(DOCKERS_DB_PATH, "rb") as dockers_db:
				self.dockers = pickle.load(dockers_db)
				return True

		return False

	def save_dockers_db(self):
		with open(DOCKERS_DB_PATH, "wb") as dockers_db:
			pickle.dump(self.dockers, dockers_db)

	def highest_docker_id(self):
		highest = -1
		for docker in self.dockers.keys():
			if docker > highest:
				highest = docker

		return highest

	def add_docker(self, ip):
		try:
			ipaddress.ip_address(ip)
		except: 
			print (f"{ip} is an invalid ip address.")
			return

		new_id = self.highest_docker_id() + 1
		self.dockers[new_id] = {"ip": ip, "latest_ack": None, "curr_config": None}
		self.save_dockers_db()

	def remove_docker(self, id):
		if not id in self.dockers.keys():
			print (f"id {id} does not exist.")
			return

		del self.dockers[id]
		self.save_dockers_db()

	def show_dockers(self):
		pprint(self.dockers, width=1)

	def docker_info(self, id):
		if not id in self.dockers.keys():
			print (f"id {id} does not exist.")
			return
			
		print ("Info: ")
		pprint(self.dockers[id], width=1)
		self.reporter.show_docker_blocks(id)
		self.reporter.show_docker_reports(id)

	def update_docker(self, docker_id, conf_id):
		if not self.configuration_manager.conf_exists(conf_id):
			print(f"conf_id {conf_id} doesnt exist!")
			return
			
		self.dockers[docker_id]["curr_config"] = conf_id
		self.logger.log(f"Updated docker id {docker_id} to conf id {conf_id}")
		self.save_dockers_db()

	def get_docker_id_from_ip(self, ip):
		for docker in self.dockers:
			if self.dockers[docker]["ip"] == ip:
				return docker

		return None

	def send_no_new_config(self, ip):
		if ip in self.conns.keys():
			self.conns[ip].send(NO_NEW_CONFIG.encode("ascii"))

	def send_config(self, ip, conf_id):
		js = self.configuration_manager.get_json_config(conf_id)

		if js is None:
			return

		if ip in self.conns.keys():
			self.conns[ip].send(js.encode("ascii"))

		self.logger.log(f"Sent config {conf_id} to ip {ip}")

	def answer_to_docker_report(self, docker_id, ip, config_id, config_creation_time):
		if not docker_id in self.dockers.keys():
			return

		if self.dockers[docker_id]["curr_config"] != config_id:
			return self.send_config(ip, self.dockers[docker_id]["curr_config"])

		if self.configuration_manager.conf_time(self.dockers[docker_id]["curr_config"]) > config_creation_time:
			return self.send_config(ip, self.dockers[docker_id]["curr_config"])

		return self.send_no_new_config(ip)			





