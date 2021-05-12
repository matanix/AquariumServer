import socket
import json

HOST = "127.0.0.1"
PORT = 4000


def block(socket):
	inp = input("Enter syscall number\n")
	try:
		num = int(inp)
		socket.sendall("BLOCKED {}".format(num).encode("ascii"))
	except Exception as e:
		print ("failed with {}".format(e))

def report(socket):
	try:
		report = {}
		report["syscalls"] = {0: 5, 2: 5, 3: 5, 7: 12}
		report["config_creation_time"] = 0
		report["config_id"] = 0
		js = json.dumps(report)
		socket.sendall(js.encode("ascii"))
		print(socket.recv(2000))
	except Exception as e:
		print (f"failed with {str(e)}")


def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))

	while True:
		inp = input("Enter b for block or r for report\n")
		if inp.startswith("b"):
			block(s)
		if inp.startswith("r"):
			report(s)

	exit()


if __name__ == "__main__":
	main()