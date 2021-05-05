import argparse
from server import Server
from cli import CLI
from log import Logger
from reporter import Reporter
from config import ConfigurationManager

def start_thread(thread_obj):
	thread_obj.setDaemon(True)
	thread_obj.start()
	
def init(args):
	configuration_manager = ConfigurationManager()

	logger = Logger(args)
	start_thread(logger)

	reporter = Reporter(args, logger)
	start_thread(reporter)

	server = Server(args, logger, reporter, configuration_manager)
	start_thread(server)

	reporter.save_server(server)

	return logger, reporter, server, configuration_manager

def run(args):
	logger, reporter, server, configuration_manager = init(args)
	cli = CLI(args, server, logger, reporter, configuration_manager)
	cli.run()

def main():
	argument_parser = argparse.ArgumentParser("Aquarium docker management server")
	args = argument_parser.parse_args()
	run(args)



if __name__ == "__main__":
	main()