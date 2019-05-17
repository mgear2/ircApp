#!/usr/bin/python
# USAGE:   client.py <HOST> <PORT>
#
# EXAMPLE: client.py localhost 8000
import socket
import sys

class Client:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.menuString = ("new - create new room\n"+
                            "list - list available rooms\n"+
                            "join <room> - join an available room\n"+
                            "speakmode - enter and exit speakmode while in a room\n"+
                            "exit - exit the program")
    
    def connect(self):
        self.socket.connect((self.host, self.port))

    def send(self, message):
        self.socket.sendall(message.encode('utf-8'))
        data = self.socket.recv(10000000)
        print(data.decode("utf-8"))
        print ('received', len(data), ' bytes')
        self.socket.close()

    def menu(self):
        print(self.menuString)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print ("USAGE: client.py <HOST> <PORT>")
        sys.exit(0)

    client = Client(sys.argv[1], int(sys.argv[2]))
    client.connect()

    while True:
        userstring = input("Enter Command(M for Menu): ")

        if userstring == "M":
            client.menu()
            continue

        client.send(userstring)

        if userstring == "exit": 
            sys.exit(0)