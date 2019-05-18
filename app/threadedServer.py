#!/usr/bin/python
# USAGE:   threadedServer.py <PORT>
#
# EXAMPLE: threadedServer.py 8000
import socket
import sys
from threading import Thread
from room import Room

class clientThread(Thread):
    def __init__(self, Server, conn, addr):
        super(clientThread, self).__init__()
        self.name = addr
        self.conn = conn
        self.server = Server

    # thread created will run this method to facilitate communication between the client and the server
    def run(self):
        self.conn.send("Welcome. Connection info: {0}".format(self.conn).encode("utf-8"))
        while True: 
            data = self.conn.recv(1000000)
            print(data)
            if data.decode("utf-8") == "exit":
                break
            #reply = "Okay: ".encode("utf8") + data
            reply = self.verify(data.decode("utf-8"))
            self.conn.sendall(reply.encode("utf-8"))
        self.conn.close()

    def verify(self, data):
        statusArray = data.split()
        keyA = statusArray[0]
        if(keyA == "new"):
            # room creation
            keyB = statusArray[1]
            self.server.newroom(keyB)
            return "Creating new room: {0}".format(keyB)
        elif(keyA == "kill"):
            # kill the server. Used for testing. 
            print("Attempting to kill {0}".format(self.server.socket))
            self.server.exit()
        elif(keyA == "list"):
            # list the clients on the server side
            self.server.list()
            # list the clients on the client side
            clientstring = ""
            for client in self.server.clients:
                clientstring += (client.name +"\n")
            return clientstring
        else:
            return "Verified"

class Server(Thread):
    def __init__(self, host, port):
        super(Server, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.clients = []
        self.rooms = []
        self.roomno = 0

    # thread created will run this method to listen for client connections
    def run(self):
        while True:
            conn, addr = self.socket.accept()
            print("Client connected: {0}".format(addr))
            newthread = clientThread(self, conn, addr)
            self.clients.append(newthread)
            newthread.start()

    # room creation
    def newroom(self, name):
        newrm = Room(name, self.roomno)
        self.roomno += 1
        self.rooms.append(newrm)

    # lists the clients on the server side
    def list(self):
        for client in self.clients:
            print(client, client.name)

    # kill the server. Used for testing. 
    def exit(self):
        self.socket.close()
        sys.exit(0)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print ("USAGE:   main.py <PORT>")
        sys.exit(0)

    # create a Server instance
    server = Server('', int(sys.argv[1]))

    # start a thread to listen for connections
    server.start()