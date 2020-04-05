from threading import Thread
from room import Room
import sys


class serverThread(Thread):
    """ Class that maintains information on the server for specific clients.

    Args:
        Server (Server) : A instance of the Server object.
        conn (Socket) : client connection information used to send/receive
            messages.
        addr (Socket) : address bound to socket on client side.
        name (str) : user name of the client.

    Attributes:
        conn (Socket) : client connection information used to send/receive
            messages.
        addr (Socket) : address bound to socket on client side.
        Server (Server) : A instance of the Server object.
        name (str) : user name of the client.
    
    """

    def __init__(self, Server, conn, addr, name):
        super(serverThread, self).__init__()
        self.conn = conn
        self.addr = addr
        self.server = Server
        self.name = name

    def run(self):
        """ Thread faciliates communication between client and server."""

        print("Client connected: {0}".format(self.addr))
        self.conn.send(
            "Welcome. Connection info: {0}".format(self.conn).encode("utf-8")
        )
        while self.server.alive:
            try:
                data = self.conn.recv(4096)
            # Handle client disconnect
            except Exception:
                print("{0} disconnected from {1}".format(self.name, self.addr))
                break
            print(data)
            if data.decode("utf-8") == "exit":
                break
            reply = self.verify(data.decode("utf-8"))
            print("Sending: " + reply)
            self.conn.sendall(reply.encode("utf-8"))
        self.disconnect()
        return

    def verify(self, data):
        """ Used to interpet strings sent by the client. 

        Args:
            data (str) : string sent by the client. The string is converted
                into a list and passed to additional functions.
        
        Returns :
            str : String reply to display to user.
        
        """

        statusArray = data.split()
        keyA = statusArray[0]
        if len(statusArray) > 1:
            keyB = statusArray[1]
        else:
            keyB = "Default"

        reply = "Verified"

        if keyA == "new":
            reply = self.new(statusArray)
        elif keyA == "kill":
            reply = self.kill()
        elif keyA == "clients":
            reply = self.clients()
        elif keyA == "rooms":
            reply = self.rooms()
        elif keyA == "join":
            reply = self.join(statusArray)
        elif keyA == "leave":
            reply = self.leave(statusArray)
        elif keyA == "members":
            reply = self.memberlist(keyB)
        elif keyA == "send":
            reply = self.send(statusArray)
        elif keyA == "tell":
            reply = self.tell(statusArray)
        return reply

    def new(self, array):
        """ Sends message to server to create new rooms.

        Args:
            array (list(str)) : list of strings.

        Returns:
            str : String to display to user whether successful or not.
        
        """

        rooms = array[1:]
        for room in rooms:
            returnval = self.server.newroom(room)
            if not returnval:
                return "Roomname {0} in use!".format(room)
        return "Creating new room: {0}".format(" ".join(room for room in rooms))

    def disconnect(self):
        """ Removes username from server and then closers connection."""

        self.server.usernames.remove(self.name)
        for room in self.server.rooms:
            current = self.server.rooms[room]
            current.remove(self.name)
        self.conn.close()
        return

    def kill(self):
        """ Kills the server. Used for testing. 
        
        Returns:
            str : Message on success.
            
        """

        print("Attempting to kill {0}".format(self.server.socket))
        self.server.exit()
        return "kill"

    def clients(self):
        """ Lists of clients on the server side.

        Returns:
            str : String of clients.
        
        """

        reply = self.server.clientlist()
        return reply

    def rooms(self):
        """ List of rooms on the server side.

        Returns:
            str : List of rooms, or message that there are no rooms.

        """

        reply = self.server.roomlist()
        if reply == "":
            reply = "No rooms"
        return reply

    def findroom(self, room):
        """ Used to locate rooms on the server.

        Args:
            room (str) : A room name.
        
        Returns:
            str : A list of rooms on the server, or message on failure.
        
        """

        try:
            room = self.server.rooms[room]
        except:
            return "Could not find {0}".format(room)
        return room

    def join(self, array):
        """ Joins specified rooms on the server.

        Args:
            array (list(str)) : a list of strings input by the user.
        
        Returns:
            str : Rooms joined or message on failure.
        
        """

        rooms = self._search_rooms(array)
        rooms = self._room_action(rooms, "add")
        retstring = "Joined "
        retstring += rooms
        return retstring

    def leave(self, array):
        """ Leaves specified rooms on the server.

        Args:
            array (list(str)) : a list of strings input by the user.
        
        Returns:
            str : Rooms joined or message on failure.
        
        """
        rooms = self._search_rooms(array)
        rooms = self._room_action(rooms, "remove", False)
        retstring = "Left "
        retstring += rooms
        return retstring

    def memberlist(self, keyB):
        """ Used to display members of a room.

        Args:
            keyB (str) : Name of the room.

        Returns: 
            str : String of members in room, or No memebers if ther are none.

        """

        room = self.findroom(keyB)
        if isinstance(room, str):
            return room

        memberstring = room.memberlist()
        if memberstring == "":
            return "No members in {0}".format(keyB)
        return memberstring

    def send(self, statusArray):
        """ Used to send messages to rooms.

        Args:
            statusArray (list(str)) : a list of strings input by user.
        
        Returns:
            str : Message reporting success or failure.
        
        """

        if "-" not in statusArray:
            return (
                "Messages should be in the form: send [room] - [msg]."
                + " Please check formatting and try again."
            )

        index = statusArray.index("-")
        rooms = self._search_rooms(statusArray[:index])

        # remove index + 1 items of the status array and converts to a string
        msg = statusArray[index + 1 :]
        msg = " ".join(msg)
        msg += "\n"
        for room in rooms:
            if isinstance(room, Room):
                room.sendall(self.name, msg)
        return ""

    def tell(self, statusArray):
        """ Sends a private message to other clients.

        Args:
            statusArray (list(str)) : a list of strings input by user.
        
        Returns:
            str : Message reporting success or failure.
        
        """

        # dest will be 2nd option in the status array
        dest = statusArray[1]
        msg = statusArray[2:]
        msg = " ".join(msg)
        msg += "\n"
        for thread in self.server.clients:
            if thread.name == dest:
                conn = thread.conn
                conn.send(
                    "{0} whispers to you : {1}".format(self.name, msg).encode("utf-8")
                )
                self.conn.send("You tell {0} : {1}".format(dest, msg).encode("utf-8"))
                return ""
        return "I'm sorry, it appears {0} is offline.".format(dest)

    def _search_rooms(self, array):
        """Searches an array of string for room names and
        returns any matches in the beginning of the array.

        Args: 
            array (list(str)): a list of strings input by user.
        
        Returns:
            list(str) : A list of string matches to room names.
        
        """

        res = []
        # Search the string for rooms
        for word in array[1:]:
            if self.findroom(word):
                res.append(self.findroom(word))
            else:
                break
        return res

    def _room_action(self, array, string, conn=True):
        """Performs a method on the room class based on parameters given.

        Args:
            array (list(str)) : a list of strings input by user.
            string (str) : a string determining which action the server should
                take. Can be either 'add' or 'remove'.
            conn (bool) : Used to determine if conn Socket should be used by
                server. Set to True by default.
        
        Returns: 
            str : Message reporting success or failure.
        """

        retrooms = []
        notfound = []
        retstring = ""
        for room in array:
            if isinstance(room, Room):
                retrooms.append(room)
                room_method = getattr(room, string)
            else:
                notfound.append(room)
                continue
            if conn:
                room_method(self.name, self.conn)
            else:
                room_method(self.name)
        if retrooms != []:
            # pylint: disable=no-member
            retstring += "{0}; ".format(" ".join(room.name for room in retrooms))
        if len(retrooms) < len(array):
            retstring += str(notfound)
        return retstring
