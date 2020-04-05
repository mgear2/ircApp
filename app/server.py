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
    """ Class that maintains information for the server in client-server 
        architecture.

    Args:
        host (str): a string representing the host. Can be Internet domain or 
                IP address.
        port (int): 16 bit unsigned integer representing port connection.

    Attributes:
        socket (Socket) : Socket class that enables communication between 
            clients.
        clients (list(serverThread)) : a list of client serverThread classes.
        usernames (list(str)) : a list of client user names.
        rooms (dict(Room)) : a dictionary of Room classes.
        roomno (int) : incrementing integer value to maintain unique room
            identifier.
        platform (str) : the OS platform set on creation
        alive (bool) : represents the current state of the server, active is 
            True.

    """

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
        """ Sets error property in Server class based on platform."""

        if self.platform == "linux":
            self.error = BlockingIOError
        elif "win" in self.platform:
            self.error = WindowsError
        return

    def run(self):
        """ Listens for client connections. Exits when alive attribute is
        modified. """

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
        return

    def newroom(self, name):
        """ Creates new Room object instances and adds to rooms dictionary.

        Args:
            name (str) : the name of the room to be created.

        Returns:
            bool : True on success, False if room name is already in use.

        """

        if name in self.rooms:
            return False
        newrm = Room(name, self.roomno)
        self.roomno += 1
        self.rooms[newrm.name] = newrm
        return True

    def clientlist(self):
        """ Lists the clients on the server side.

        Returns:
            str : A string with name of all active clients.
        """

        clientstring = ""
        for client in self.clients:
            clientstring += client.name + "\n"
            print(client, client.name)
        return clientstring

    def roomlist(self):
        """ Lists the rooms on the server side.

        Returns:
            str : A string of all the rooms names.

        """

        roomstring = ""
        for room in self.rooms:
            roomstring += room + "\n"
            print(room)
        return roomstring

    def exit(self):
        """ Kills the server. Used for testing. """

        print("Server: Connection closed; exiting...")
        self.alive = False
        self.socket.close()
        sys.exit(0)
        return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE:   main.py <PORT>")
        sys.exit(0)

    server = Server("", int(sys.argv[1]))
    server.start()
