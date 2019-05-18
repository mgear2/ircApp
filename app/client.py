#!/usr/bin/python
# USAGE:   client.py <HOST> <PORT>
#
# EXAMPLE: client.py localhost 8000
import socket
import sys

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.menuString = ("new <title> - create new room with name <title>\n"+
                            "list - list available rooms\n"+
                            "join <room> - join an available room\n"+
                            "speakmode - enter and exit speakmode while in a room\n"+
                            "kill - kill the server\n"+
                            "exit - exit the program")
    
    # create a socket instance and connect
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.send("Hello")

    # send a message to server, print reply details to client
    def send(self, message):
        self.socket.sendall(message.encode('utf-8'))
        data = self.socket.recv(10000000)
        print(data.decode("utf-8") + '; received '+ str(len(data)) + ' bytes')

    # print out a menu to instruct users in app usage
    def menu(self):
        print(self.menuString)

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print ("USAGE: client.py <HOST> <PORT>")
        sys.exit(0)

    client = Client(sys.argv[1], int(sys.argv[2]))
    client.connect()

    while True:
        userstring = input("Enter Command (M for Menu): ")

        if userstring == "M":
            client.menu()
            continue

        # an empty userstring will cause errors if sent to the server
        if userstring == "":
            continue

        client.send(userstring)

        if userstring == "exit":
            client.socket.close()
            sys.exit(0)