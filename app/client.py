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
    """Client class used to hold information about the client.

    Args:
        host (str): a string representing the host. Can be Internet domain or 
                IP address.
        port (int): 16 bit unsigned integer representing port connection.

    Attributes:
        socket (socket): a socket object used in connecting to server.
        host (str): a string representing the host. Can be Internet domain or 
                IP address.
        port (int): 16 bit unsigned integer representing port connection.
        name (str): 20 character username.
        menuString (str): a string containing menu information.
        rooms (list(str)): list of rooms that the client has access to.
        platform (str): a string that contains client OS platform.
        alive (bool): represents the current state of the client, active is 
            True.

    """

    def __init__(self, host, port):
        super(Client, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.name = self.username()
        self.menuString = ("new [room] ([room] ...) : create new room with" 
                            + " specified name\n"
                            "join [room] ([room] ...)   : join the selected"
                            + " room(s)\n"+
                            "leave [room] ([room] ...)  : leave the selected"
                            + " room(s)\n"+
                            "send [room] ([room] ...) - [msg]   : send message" 
                            + " to a selected room(s)\n"+
                            "rooms  : list available rooms\n"+
                            "members [room]     : list the members of a room\n"
                            "clients    : list of clients from server" 
                            + " directory\n"
                            "kill   : kill the server\n"+
                            "exit   : exit the program\n")
        self.rooms = []
        self.platform = sys.platform
        self.seterror()
        self.alive = True
    
    def commandline(self):
        """ Function used to maintain user input"""

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
        """ Function that connects and maintains connection with server """

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
                    print("10038/10053/10054/9: Connection terminated" 
                    + " by server;")
                    self.exit()
                else:
                    print("Caught: " + str(e))
                    self.exit()

    def send(self, message):
        """ Sends a message to server, prints reply details to client

        Args:
            message (str) : string that contains message to send to server.

        """

        try:
            self.socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print("Connection with server lost with error {0}".format(e))
            self.exit()
        if message == "kill" or message == "exit":
            self.exit()

    def verify(self, message):
        """ Interprets message received by server.

        Args:
            message (int) : a bit-stream server message.

        Returns:
            displays decoded message on success
            exits if NAMEERROR is found

        """

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
        """ Ensures that the I/O is non-blocking for windows."""

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
            # Removed continue
    
    def input_linux(self):
        """ Ensures that the I/O is non-blocking for linux."""

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

    def menu(self):
        """ Displays a menu to instruct users in app usage."""

        print(self.menuString)

    def exit(self):
        """ Exits the program and closes connection with the server."""

        print("Exiting...")
        self.alive = False
        self.socket.close()
        sys.exit(0)

    def seterror(self):
        """" Determines the type of errors to set based on user's platform."""

        if self.platform == "linux":
            self.error = BlockingIOError
        elif "win" in self.platform:
            self.error = WindowsError

    def username(self):
        """ Creates a screenname for the user.

        Returns:
            str: A user screenname.
            Displays error message if not successful.
        """

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