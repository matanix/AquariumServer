import traceback

CLI_SIGN = ">"
HELP_COMMAND = "help"
EXIT_COMMAND = "exit"
SHOW_LOG_COMMAND = "logs"
SHOW_REPORTS_COMMAND = "reports"
SHOW_DOCKERS_COMMAND = "dockers"
ADD_DOCKER_COMMAND = "docker add"
REM_DOCKER_COMMAND = "docker rem"
DOCKER_INFO_COMMAND = "docker info"
REM_CONFIG_COMMAND = "conf rem"
CREATE_CONFIG_COMMAND = "conf create"
UPDATE_DOCKER_COMMAND = "docker update"
SHOW_CONFIGS_COMMAND = "configs"
SHOW_BLOCKS_COMMAND = "blocks"
CONF_INFO_COMMAND = "conf info"
INVALID_PARAMETERS = "Invalid parameters."
HELP_FORMAT = "{} -> {}"
UNKNOWN_COMMAND = "Unknown command."

class CLI():
	def __init__(self, args, server, logger, reporter, configuration_manager):
		self.args = args
		self.server = server
		self.logger = logger
		self.reporter = reporter
		self.configuration_manager = configuration_manager

	def help(self, inp):
		if inp != HELP_COMMAND:
			return False

		print (HELP_FORMAT.format(HELP_COMMAND, "print this message"))
		print (HELP_FORMAT.format(EXIT_COMMAND, "terminate"))
		print (HELP_FORMAT.format(SHOW_LOG_COMMAND, "show {num} latest logs"))
		print (HELP_FORMAT.format(SHOW_DOCKERS_COMMAND, "show dockers info"))
		print (HELP_FORMAT.format(ADD_DOCKER_COMMAND, "add docker with {ip} to the server to monitor"))
		print (HELP_FORMAT.format(REM_DOCKER_COMMAND, "remove docker {id} from server"))
		print (HELP_FORMAT.format(DOCKER_INFO_COMMAND, "show {id} docker info"))
		print (HELP_FORMAT.format(UPDATE_DOCKER_COMMAND, "update docker {docker_id} conf to {conf_id}"))
		print (HELP_FORMAT.format(REM_CONFIG_COMMAND, "remove config {id}"))
		print (HELP_FORMAT.format(CREATE_CONFIG_COMMAND, "create a new config"))
		print (HELP_FORMAT.format(SHOW_CONFIGS_COMMAND, "show all configurations"))
		print (HELP_FORMAT.format(CONF_INFO_COMMAND, "show conf {id} info"))
		print (HELP_FORMAT.format(SHOW_REPORTS_COMMAND, "show all reports"))
		print (HELP_FORMAT.format(SHOW_BLOCKS_COMMAND, "show all blocks"))
		return True

	def exit(self, inp):
		if not inp.startswith(EXIT_COMMAND):
			return False

		exit()

	def get_params(self, inp, command):
		prefix = command + " "

		if not inp.startswith(prefix):
			return None

		return inp.replace(prefix, "").split(' ')

	def show_log(self, inp):
		if not inp.startswith(SHOW_LOG_COMMAND):
			return False

		try:
			params = self.get_params(inp, SHOW_LOG_COMMAND)
			num_of_logs = int(params[0])
		except:
			print (INVALID_PARAMETERS)
			return True

		self.logger.show_logs(num_of_logs)
		return True

	def show_reports(self, inp):
		if not inp.startswith(SHOW_REPORTS_COMMAND):
			return False

		self.reporter.show_reports()
		return True

	def show_blocks(self, inp):
		if not inp.startswith(SHOW_BLOCKS_COMMAND):
			return False

		self.reporter.show_blocks()
		return True

	def update_docker(self, inp):
		if not inp.startswith(UPDATE_DOCKER_COMMAND):
			return False

		try:
			params = self.get_params(inp, UPDATE_DOCKER_COMMAND)
			docker_id = int(params[0])
			conf_id = int(params[1])
		except:
			print (INVALID_PARAMETERS)
			return True

		self.server.update_docker(docker_id, conf_id)
		return True

	def show_dockers(self, inp):
		if not inp.startswith(SHOW_DOCKERS_COMMAND):
			return False

		self.server.show_dockers()
		return True

	def add_docker(self, inp):
		if not inp.startswith(ADD_DOCKER_COMMAND):
			return False

		try:
			params = self.get_params(inp, ADD_DOCKER_COMMAND)
			ip = params[0]
		except:
			print (INVALID_PARAMETERS)
			return True

		self.server.add_docker(ip)
		return True

	def remove_docker(self, inp):
		if not inp.startswith(REM_DOCKER_COMMAND):
			return False

		try:
			params = self.get_params(inp, REM_DOCKER_COMMAND)
			id = int(params[0])
		except:
			print (INVALID_PARAMETERS)
			return True

		self.server.remove_docker(id)
		return True

	def docker_info(self, inp):
		if not inp.startswith(DOCKER_INFO_COMMAND):
			return False

		try:
			params = self.get_params(inp, DOCKER_INFO_COMMAND)
			docker_id = int(params[0])
		except:
			print (INVALID_PARAMETERS)
			return True

		self.server.docker_info(docker_id)
		return True

	def create_config(self, inp):
		if not inp.startswith(CREATE_CONFIG_COMMAND):
			return

		self.configuration_manager.create_config()
		return True

	def rem_config(self, inp):
		if not inp.startswith(REM_CONFIG_COMMAND):
			return False

		try:
			params = self.get_params(inp, REM_CONFIG_COMMAND)
			conf_id = int(params[0])
		except:
			print (INVALID_PARAMETERS)
			return True

		self.configuration_manager.remove_config(conf_id)
		return True

	def conf_info(self, inp):
		if not inp.startswith(CONF_INFO_COMMAND):
			return False

		try:
			params = self.get_params(inp, CONF_INFO_COMMAND)
			conf_id = int(params[0])
		except:
			print (INVALID_PARAMETERS)
			return True

		self.configuration_manager.show_config(conf_id)
		return True

	def show_configs(self, inp):
		if not inp.startswith(SHOW_CONFIGS_COMMAND):
			return False

		self.configuration_manager.show_all()
		return True


	def execute(self, inp):
		if self.help(inp):
			return

		elif self.exit(inp):
			return
		
		elif self.show_log(inp):
			return

		elif self.show_reports(inp):
			return

		elif self.update_docker(inp):
			return

		elif self.show_dockers(inp):
			return

		elif self.add_docker(inp):
			return

		elif self.remove_docker(inp):
			return

		elif self.docker_info(inp):
			return

		elif self.create_config(inp):
			return

		elif self.rem_config(inp):
			return

		elif self.conf_info(inp):
			return

		elif self.show_configs(inp):
			return

		elif self.show_blocks(inp):
			return

		print (UNKNOWN_COMMAND)

	def is_empty(self, inp):
		if len(inp.replace('\n', '').replace('\t', '').replace('\r', '')) == 0:
			return True

	def run(self):
		print ("Welcome to aquarium docker server.")
		self.help(HELP_COMMAND)

		while True:
			inp = input(CLI_SIGN)

			if self.is_empty(inp):
				continue
			try:
				self.execute(inp)

			except Exception as e:
				print (str(e))	
				traceback.print_exc()