#!/usr/bin/python
# USAGE:   client.py <HOST> <PORT>
#
# EXAMPLE: client.py localhost 8000
import socket
import sys
import errno
import select
if "win" in sys.platform:
    import msvcrt
import time
from time import sleep
from threading import Thread

class Client(Thread):
    def __init__(self, host, port):
        super(Client, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.name = self.username()
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
        self.alive = True
    
    def commandline(self):
        print("Enter Command (M for Menu)")
        while self.alive:
            userstring = []

            if self.platform == "linux":
                userstring = self.input_linux()
            elif "win" in self.platform:
                userstring = self.input_windows()

            if userstring == [] or userstring == None:
                continue

            userstring = ''.join(userstring)

            if userstring == "M":
                self.menu()
                continue

            print("Sending: " + userstring)
            self.send(userstring)
        return

    def run(self):
        try:
            self.socket.connect((self.host, self.port))
            self.send(self.name)
            data = self.socket.recv(4096)
        except Exception as e:
            print("Connection error: {0}".format(e))
            self.exit()
        self.verify(data)
        self.socket.setblocking(False)
        sleep(1)

        while self.alive:
            try:
                data = self.socket.recv(4096)
                self.verify(data)
                if len(data) == 0:
                    print("Data = 0; Connection terminated by server;")
                    self.exit()
            except Exception as e: 
                err = e.args[0]
                # if no data was received by the socket
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    sleep(0.5)
                    continue
                # Handle terminated connection
                elif err == 10038 or err == 10053 or err == 10054 or err == 9:
                    print("10038/10053/10054/9: Connection terminated by server;")
                    self.exit()
                else:
                    print("Caught: " + str(e))
                    self.exit()

    # send a message to server, print reply details to client
    def send(self, message):
        try:
            self.socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print("Connection with server lost with error {0}".format(e))
            self.exit()
        if message == "kill" or message == "exit":
            self.exit()

    def verify(self, message):
        message = message.decode("utf-8")
        if message == "":
            return
        if message == "NAMEERROR":
            print("Error: Name in use! Please select a different name")
            self.exit()
        print(message + '; received '+ str(len(message)) + ' bytes')
        statusArray = message.split()
        if statusArray[0] == "Joined":
            self.rooms.append(statusArray[1])

    def input_windows(self):
        userstring = []
        while self.alive:
            print("> " + ''.join(userstring), end='', flush=True)
            t0 = time.time()
            while time.time() - t0 < 1:
                if msvcrt.kbhit():
                    character = msvcrt.getch()
                    char_decode = character.decode("utf-8")
                    if char_decode == '\b':
                        if len(userstring) > 0:
                            sys.stdout.write("\b")
                            sys.stdout.write(" ")
                            sys.stdout.flush()
                            del userstring[-1]
                        msvcrt.putch(character)
                        continue
                    elif char_decode == '\r':
                        print("\n")
                        return userstring
                    msvcrt.putch(character)
                    userstring.append(char_decode)
                time.sleep(0.1)
            sys.stdout.write("\r")
            continue
    
    def input_linux(self):
        userstring = []
        sleep(0.5)
        print("> ", end='', flush=True)
        while self.alive:
            userinput = select.select([sys.stdin], [], [], 1)[0]
            if userinput:
                line = sys.stdin.readline()
                line = list(line)
                if '\n' in line:
                    userstring.append(line[:-1])
                    userstring = userstring[0]
                    break
        return userstring

    # print out a menu to instruct users in app usage
    def menu(self):
        print(self.menuString)

    def exit(self):
        print("Exiting...")
        self.alive = False
        self.socket.close()
        sys.exit(0)

    def seterror(self):
        if self.platform == "linux":
            self.error = BlockingIOError
        elif "win" in self.platform:
            self.error = WindowsError

    def username(self):
        while True:
            screenName = input("Enter desired screenname: ")
            if len(screenName) <= 20:
                return screenName
            print("Please select a username of 20 characters or less")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print ("USAGE: client.py <HOST> <PORT>")
        sys.exit(0)

    host = sys.argv[1]
    port = int(sys.argv[2])
    #screenName = username()

    client = Client(host, port)
    client.start()
    client.commandline()

    sys.exit(0)