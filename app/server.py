#!/usr/bin/python
# USAGE:   server.py <PORT>
#
# EXAMPLE: server.py 8000
import socket
import sys
from room import Room

class Server:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.rooms = []
        self.roomno = 0

    def bind(self):
        self.socket.bind((self.host, self.port))

    def listen(self):
        self.socket.listen(5)

    def connect(self):
        self.conn, self.addr = self.socket.accept()

    def disconnect(self):
        self.conn.close()
        self.socket.close()

    def serve(self):
        print ('client is at', self.addr)
        data = self.conn.recv(1000000)
        status = data.decode("utf-8")
        updata = self.verify(status).encode("utf-8")
        print ('sending data ', updata)
        self.conn.send(updata)
        return status

    def verify(self, status):
        if(status == ""):
            return "Verified"
        statusArray = status.split()
        if(statusArray[0] == "new"):
            self.newroom(statusArray[1])
            return "Creating new room: {0}".format(statusArray[1])
        return "Verified"

    def newroom(self, name):
        newrm = Room(name, self.roomno)
        self.roomno += 1
        self.rooms.append(newrm)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print ("USAGE:   main.py <PORT>")
        sys.exit(0)

    server = Server('', int(sys.argv[1]))
    server.bind()
    server.listen()
    server.connect()

    while (1):
        status = server.serve()
        print("Status: {0}".format(status))
        if status == "exit":
            server.disconnect()
            sys.exit(0)