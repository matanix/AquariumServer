from queue import Queue
from datetime import datetime
import threading

LOG_FILE_PATH = "logs/log.txt"
LOG_FORMAT = "{}: {}\n"
SANITY_LOG_SIZE = 5

class Logger(threading.Thread):
	def __init__(self, args):
		threading.Thread.__init__(self)
		self.args = args
		self.log_file = open(LOG_FILE_PATH, "a+")
		self.queue = Queue()

	def log(self, msg):
		now = datetime.now()
		dt = now.strftime("%d/%m/%Y %H:%M:%S")
		log_msg = LOG_FORMAT.format(dt, msg) 
		self.queue.put(log_msg)

	def show_logs(self, num):
		self.read_file = open(LOG_FILE_PATH, "r")
		lines = self.read_file.read().split('\n')
		lines = [line for line in lines if len(line) > SANITY_LOG_SIZE]

		if len(lines) < num:
			num = len(lines)	

		print (f"Displaying {num} lines")

		lines = lines[-num:]

		for line in lines:
			print (line)

		print ("Done!")


	def run(self):
		while True:
			log_msg = self.queue.get()
			self.log_file.write(log_msg)
			self.log_file.flush()
