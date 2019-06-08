#!/usr/bin/python
# USAGE:   client.py <HOST> <PORT>
#
# EXAMPLE: client.py localhost 8000
import socket
import sys
import errno
from time import sleep
from threading import Thread

class Client(Thread):
    def __init__(self, host, port, name):
        super(Client, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.name = name
        self.menuString = ("new <title> - create new room with <title>\n"+
                            "join <room> - join a selected room\n"+
                            "leave <room> - leave a selected room\n"+
                            "leave <room> <msg> - send message to a selected room\n"+
                            "rooms - list available rooms\n"+
                            "members <room> - list the members of a room"
                            "clients - list of clients from server directory\n"
                            "kill - kill the server\n"+
                            "exit - exit the program")
        self.rooms = []
        self.platform = sys.platform
        self.seterror()
    
    def seterror(self):
        if self.platform == "linux":
            self.error = BlockingIOError
        elif "win" in self.platform:
            self.error = WindowsError

    # send a message to server, print reply details to client
    def send(self, message):
        self.socket.sendall(message.encode('utf-8'))

    def verify(self, message):
        message = message.decode("utf-8")
        if message == "":
            return
        print(message + '; received '+ str(len(message)) + ' bytes')
        statusArray = message.split()
        if statusArray[0] == "Joined":
            self.rooms.append(statusArray[1])

    def run(self):
        self.socket.connect((self.host, self.port))
        data = self.socket.recv(4096)
        self.verify(data)
        self.socket.setblocking(False)
        sleep(0.5)
        self.send(self.name)

        while True:
            try:
                data = self.socket.recv(4096)
                self.verify(data)
            except (socket.error, self.error) as e: 
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

    # print out a menu to instruct users in app usage
    def menu(self):
        print(self.menuString)

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print ("USAGE: client.py <HOST> <PORT>")
        sys.exit(0)

    while True:
        screenName = input("Enter desired screenname: ")
        if len(screenName) <= 20:
            break
        print("Please select a username of 20 characters or less")

    client = Client(sys.argv[1], int(sys.argv[2]), screenName)
    client.start()

    print("Enter Command (M for Menu)")

    while True:
        sleep(0.5)
        userstring = input("> ")

        # an empty userstring will cause errors if sent to the server
        if userstring == "":
            continue

        if userstring == "M":
            client.menu()
            continue

        client.send(userstring)

        if userstring == "exit":
            client.socket.close()
            sys.exit(0)