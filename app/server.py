#!/usr/bin/python
# USAGE:   threadedServer.py <PORT>
#
# EXAMPLE: threadedServer.py 8000
import socket
import sys
from threading import Thread
from room import Room
from clientThread import clientThread

class Server(Thread):
    def __init__(self, host, port):
        super(Server, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.clients = []
        self.rooms = {}
        self.roomno = 0
        self.newroom("Default")

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
        if name in self.rooms:
            return False
        newrm = Room(name, self.roomno)
        self.roomno += 1
        self.rooms[newrm.name] = newrm
        return True

    # lists the clients on the server side
    def clientlist(self):
        clientstring = ""
        for client in self.clients:
            clientstring += (client.name +"\n")
            print(client, client.name)
        return clientstring

    # lists the clients on the server side
    def roomlist(self):
        roomstring = ""
        for room in self.rooms:
            roomstring += (room + "\n")
            print(room)
        return roomstring

    # kill the server. Used for testing. 
    def exit(self):
        self.socket.close()
        sys.exit(0)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print ("USAGE:   main.py <PORT>")
        sys.exit(0)

    # create a Server instance
    serverthread = Server('', int(sys.argv[1]))

    # start a thread to listen for connections
    serverthread.start()