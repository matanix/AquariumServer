from queue import Queue
from datetime import datetime
import threading
import pickle
import os
from pprint import pprint
import json

REPORTS_DB_PATH = "db/reports"
BLOCKS_DB_PATH = "db/blocks"
BLOCKED_PREFIX = "BLOCKED "

class Reporter(threading.Thread):
	def __init__(self, args, logger):
		threading.Thread.__init__(self)
		self.args = args
		self.logger = logger
		self.queue = Queue()

		if not self.load_reports_db():
			self.reports = {}
			self.save_reports_db()

		if not self.load_blocks_db():
			self.blocks = {}
			self.save_blocks_db()

	def save_server(self, server):
		self.server = server

	def load_reports_db(self):
		if os.path.isfile(REPORTS_DB_PATH):
			with open(REPORTS_DB_PATH, "rb") as reports_db:
				self.reports = pickle.load(reports_db)
				return True

		return False

	def save_reports_db(self):
		with open(REPORTS_DB_PATH, "wb") as reports_db:
			pickle.dump(self.reports, reports_db)

	def load_blocks_db(self):
		if os.path.isfile(BLOCKS_DB_PATH):
			with open(BLOCKS_DB_PATH, "rb") as blocks_db:
				self.blocks = pickle.load(blocks_db)
				return True

		return False

	def save_blocks_db(self):
		with open(BLOCKS_DB_PATH, "wb") as blocks_db:
			pickle.dump(self.blocks, blocks_db)

	def is_block_msg(self, msg):
		if str(msg).startswith(BLOCKED_PREFIX):
			return True

		return False

	def enqueue(self, addr, msg):
		now = datetime.now()
		dt = now.strftime("%d/%m/%Y %H:%M:%S")
		self.queue.put((dt, addr, msg))

	def handle_report(self, dt, addr, report_msg):
		js = json.loads(report_msg)

		try:
			js["syscalls"]
			int(js["config_creation_time"])
			int(js["config_id"])

		except:
			self.logger.log(f"invalid report from docker ip {addr}, skipping")

		docker_id = self.server.get_docker_id_from_ip(addr[0])

		if docker_id is None:
			self.logger.log(f"report from unknown docker ip {addr}, skipping")
			return

		if docker_id in self.reports:
			self.reports[docker_id].append((dt, js))
		else:
			self.reports[docker_id] = [(dt, js)]

		self.save_reports_db()

		self.server.answer_to_docker_report(docker_id, addr, js["config_id"],  js["config_creation_time"])

	def handle_block(self, dt, addr, block_msg):
		try:
			syscall = int(block_msg.replace(BLOCKED_PREFIX, ""))
		except:
			self.logger.log(f"invalid block from docker ip {addr}, skipping")
			return

		docker_id = self.server.get_docker_id_from_ip(addr[0])

		if docker_id is None:
			self.logger.log(f"block from unknown docker ip {addr}, skipping")
			return

		if docker_id in self.blocks:
			self.blocks[docker_id].append((dt, syscall))
		else:
			self.blocks[docker_id] = [(dt, syscall)]

		self.save_blocks_db()

	def show_blocks(self):
		pprint(self.blocks, width = 1)

	def show_docker_blocks(self, docker_id):
		if docker_id in self.blocks.keys():
			print ("Blocks:")
			pprint(self.blocks[docker_id], width=1)
		else:
			print ("No blocks.")

	def show_reports(self):
		pprint(self.reports, width = 1)

	def show_docker_reports(self, docker_id):
		if docker_id in self.reports.keys():
			print ("Reports:")
			pprint(self.reports[docker_id], width=1)
		else:
			print ("No reports.")

	def run(self):
		while True:
			dt, addr, msg = self.queue.get()
			msg = msg.decode("ascii", "ignore")

			try:
				if self.is_block_msg(msg):
					self.handle_block(dt, addr, msg)
				else:
					self.handle_report(dt, addr, msg)

			except Exception as e:
				self.logger.log(f"Failed to handle msg from {addr}")
				print (str(e))

