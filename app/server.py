#!/usr/bin/python
# USAGE:   threadedServer.py <PORT>
#
# EXAMPLE: threadedServer.py 8000
import socket
import sys
import errno
from time import sleep
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
        self.usernames = []
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
        self.socket.setblocking(False)
        while self.alive:
            try:
                conn, addr = self.socket.accept()
                conn.setblocking(True)
            except Exception as e:
                err = e.args[0]
                # if no data was received by the socket
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    sleep(0.5)
                    continue
                # Handle terminated connection
                if err == 10038 or err == 10053 or err == 9:
                    print("Connection closed; exiting...")
                    break
                else:
                    print("Caught: " + str(e))
                    break
            username = conn.recv(4096).decode("utf=8")
            if username in self.usernames:
                conn.send("NAMEERROR".encode("utf-8"))
            else:
                self.usernames.append(username)
                newthread = serverThread(self, conn, addr, username)
                self.clients.append(newthread)
                newthread.start()
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
        print("Server: Connection closed; exiting...")
        self.alive = False
        self.socket.close()
        sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("USAGE:   main.py <PORT>")
        sys.exit(0)

    server = Server('', int(sys.argv[1]))
    server.start()