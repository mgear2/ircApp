#!/usr/bin/python
# USAGE:   threadedServer.py <PORT>
#
# EXAMPLE: threadedServer.py 8000
import socket
import sys
import threading
from room import Room

class Server(threading.Thread):
    def __init__(self, host, port):
        super(Server, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.clients = []
        self.rooms = []
        self.roomno = 0

    def run(self):
        while True:
            self.conn, self.addr = self.socket.accept()
            print("Client connected: {0}".format(self.addr))
            self.clients.append(self.addr)
            data = self.conn.recv(1000000)
            status = data.decode("utf-8")
            updata = self.verify(status).encode("utf-8")
            print ('sending data ', updata)
            self.conn.send(updata)

    def verify(self, status):
        statusArray = status.split()
        if(statusArray[0] == "new"):
            self.newroom(statusArray[1])
            return "Creating new room: {0}".format(statusArray[1])
        if(statusArray[0] == "exit"):
            self.conn.close()
            self.socket.close()
            sys.exit(0)
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
    server.start()