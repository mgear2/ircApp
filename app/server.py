#!/usr/bin/python
# USAGE:   threadedServer.py <PORT>
#
# EXAMPLE: threadedServer.py 8000
import socket
import sys
import errno
import sleep
from threading import Thread
from room import Room
from serverThread import serverThread

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
        self.platform = sys.platform
        self.seterror()
        self.alive = True

    def seterror(self):
        if self.platform == "linux":
            self.error = BlockingIOError
        elif "win" in self.platform:
            self.error = WindowsError

    # thread created will run this method to listen for client connections
    def run(self):
        while self.alive:
            try:
                conn, addr = self.socket.accept()
            except (socket.error, self.error) as e: 
                err = e.args[0]
                err = e.args[0]
                # if no data was received by the socket
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    sleep(0.5)
                    continue
                # if an operation was attempted on something not a socket or host aborts connection
                if err == 10038 or err == 10053 or err == 9:
                    print("Connection closed; exiting...")
                    break
                else:
                    print("Caught: " + str(e))
                    break
            print("Client connected: {0}".format(addr))
            newthread = serverThread(self, conn)
            self.clients.append(newthread)
            newthread.start()
        print("Exit reached in server.run()")
        sys.exit(0)

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

    # lists the rooms on the server side
    def roomlist(self):
        roomstring = ""
        for room in self.rooms:
            roomstring += (room + "\n")
            print(room)
        return roomstring

    # kill the server. Used for testing. 
    def exit(self):
        self.alive = False
        print("Alive: {0}".format(self.alive))
        self.socket.close()
        print("exit reached in server.exit()")
        sys.exit(0)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print ("USAGE:   main.py <PORT>")
        sys.exit(0)

    # create a Server instance
    server = Server('', int(sys.argv[1]))

    # start a thread to listen for connections
    server.start()