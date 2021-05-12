import json
import pickle
import os
from pprint import pprint
from time import time
from datetime import datetime

CONFIGS_DB_PATH = "db/configs"

class ConfigurationManager():
	def __init__(self):
		if not self.load_configs_db():
			self.configs = {}
			self.save_configs_db()

	def load_configs_db(self):
		if os.path.isfile(CONFIGS_DB_PATH):
			with open(CONFIGS_DB_PATH, "rb") as configs_db:
				self.configs = pickle.load(configs_db)
				return True

		return False

	def save_configs_db(self):
		with open(CONFIGS_DB_PATH, "wb") as configs_db:
			pickle.dump(self.configs, configs_db)

	def conf_exists(self, conf_id):
		if conf_id in self.configs.keys():
			return True

		return False

	def highest_conf_id(self):
		highest = -1
		for conf in self.configs.keys():
			if conf > highest:
				highest = conf

		return highest

	def user_get_process_names(self):
		processes_list = []

		while True:
			inp = input("Enter process name or \"next\" to the next step\n")

			if len(inp.replace(' ', '')) == 0:
				continue

			if inp == "next":
				return processes_list

			processes_list.append(inp)
			print (processes_list)

	def user_get_blocked_syscalls_list(self):
		blocked_syscalls_list = []

		while True:
			inp = input("Enter syscall num or \"end\" to finish\n")

			if len(inp.replace(' ', '')) == 0:
				continue

			if inp == "end":
				return blocked_syscalls_list

			try:
				blocked_syscalls_list.append(int(inp))
			except:
				print ("Please enter a valid number..")
				continue

			print (blocked_syscalls_list)

	def create_config(self):
		new_id = self.highest_conf_id() + 1
		processes_list = self.user_get_process_names()
		blocked_syscalls_list = self.user_get_blocked_syscalls_list()

		now = datetime.now()
		dt = now.strftime("%d/%m/%Y %H:%M:%S")

		conf = {"processes": processes_list, "blocked_syscalls": blocked_syscalls_list, "time": int(time())}
		self.configs[new_id] = conf
		self.save_configs_db()

	def show_all(self):
		pprint(self.configs, width = 1)

	def remove_config(self, conf_id):
		if not conf_id in self.configs.keys():
			print(f"conf_id {conf_id} does not exist.")
			return

		del self.configs[conf_id]
		self.save_configs_db()

	def show_config(self, conf_id):
		if not conf_id in self.configs.keys():
		 	print(f"conf_id {conf_id} does not exist.")
		 	return

		pprint(self.configs[conf_id])

	def get_json_config(self, conf_id):
		if not conf_id in self.configs.keys():
		 	return None

		return json.dumps(self.configs[conf_id])

	def conf_time(self, conf_id):
		if not conf_id in self.configs.keys():
			return 0

		return self.configs[conf_id]["time"]

		





