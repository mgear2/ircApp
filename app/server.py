#!/usr/bin/python
# USAGE:   server.py <PORT>
#
# EXAMPLE: server.py 8000
import socket
import sys

class Server:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def bind(self):
        self.socket.bind((self.host, self.port))

    def listen(self):
        self.socket.listen(1)

    def serve(self):
        conn, addr = self.socket.accept()
        print ('client is at', addr)
        data = conn.recv(1000000)
        status = data.decode("utf-8")
        updata = data
        print ('sending data ', updata)
        conn.send(updata)
        conn.close()
        return status

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print ("USAGE:   main.py <PORT>")
        sys.exit(0)

    server = Server('', int(sys.argv[1]))
    server.bind()
    server.listen()
    
    while (1):
        status = server.serve()
        print("Status: {0}".format(status))
        if status == "exit":
            sys.exit(0)