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
        self.exitflag = False
    
    def exit(self):
        self.exitflag = True
        self.socket.close()
        sys.exit(0)

    def seterror(self):
        if self.platform == "linux":
            self.error = BlockingIOError
        elif "win" in self.platform:
            self.error = WindowsError

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
        print(message + '; received '+ str(len(message)) + ' bytes')
        statusArray = message.split()
        if statusArray[0] == "Joined":
            self.rooms.append(statusArray[1])

    def run(self):
        try:
            self.socket.connect((self.host, self.port))
        except Exception as e:
            print(e)
            print("Could not connect")
            self.exit()
        print("1")
        data = self.socket.recv(4096)
        self.verify(data)
        self.socket.setblocking(False)
        sleep(0.5)
        self.send(self.name)

        while True:
            try:
                data = self.socket.recv(4096)
                self.verify(data)
                if len(data) == 0:
                    print("Data = 0; Connection terminated by server; exiting...")
                    self.exit()
            #except (socket.error, self.error) as e: 
            except Exception as e: 
                err = e.args[0]
                # if no data was received by the socket
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    sleep(0.5)
                    continue
                # if an operation was attempted on something not a socket or host aborts connection
                elif err == 10038 or err == 10053 or err == 10054 or err == 9:
                    print("10038/10053/10054/9: Connection terminated by server; exiting...")
                    self.exit()
                else:
                    print("Caught: " + str(e))
                    self.exit()

    # print out a menu to instruct users in app usage
    def menu(self):
        print(self.menuString)

def input_windows():
    userstring = []
    while client.exitflag == False:
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
    
def input_linux():
    userstring = []
    sleep(0.5)
    print("> ", end='', flush=True)
    while client.exitflag == False:
        userinput = select.select([sys.stdin], [], [], 1)
        if userinput:
            line = sys.stdin.readline()
            line = list(line)
            if '\n' in line:
                userstring.append(line[:-1])
                userstring = userstring[0]
                break
    return userstring

def getnamelist():
    return

def username():
    while True:
        screenName = input("Enter desired screenname: ")
        if len(screenName) <= 20:
            return screenName
        print("Please select a username of 20 characters or less")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print ("USAGE: client.py <HOST> <PORT>")
        sys.exit(0)

    screenName = username()

    client = Client(sys.argv[1], int(sys.argv[2]), screenName)
    client.start()

    print("Enter Command (M for Menu)")
    exitflag = False

    while client.exitflag == False:
        userstring = []

        if client.platform == "linux":
            userstring = input_linux()
        elif "win" in client.platform:
            userstring = input_windows()

        if userstring == [] or userstring == None:
            continue

        userstring = ''.join(userstring)

        if userstring == "M":
            client.menu()
            continue

        print("Sending: " + userstring)
        client.send(userstring)