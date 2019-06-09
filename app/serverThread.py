from threading import Thread
from room import Room
import sys

class serverThread(Thread):
    def __init__(self, Server, conn):
        super(serverThread, self).__init__()
        self.conn = conn
        self.server = Server

    # thread created will run this method to facilitate communication between the client and the server
    def run(self):
        self.conn.send("Welcome. Connection info: {0}".format(self.conn).encode("utf-8"))
        self.name = self.conn.recv(4096).decode("utf=8")
        while self.server.alive: 
            data = self.conn.recv(4096)
            print(data)
            if data.decode("utf-8") == "exit":
                break
            reply = self.verify(data.decode("utf-8"))
            print("Sending: " + reply)
            self.conn.sendall(reply.encode("utf-8"))
        self.disconnect()

    def verify(self, data):
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
        # room creation
        rooms = array[1:]
        for room in rooms:
            returnval = self.server.newroom(room)
            if not returnval:
                return "Roomname {0} in use!".format(room)
        return "Creating new room: {0}".format(' '.join(room for room in rooms))

    def kill(self):
        # kill the server. Used for testing. 
        print("Attempting to kill {0}".format(self.server.socket))
        self.server.exit()
        return "kill"

    def clients(self):
        # list the clients on both client and server side
        reply = self.server.clientlist()
        return reply

    def rooms(self):
        # list the croomslients on both client and server side
        reply = self.server.roomlist()
        if reply == "":
            reply = "No rooms"
        return reply

    def findroom(self, room):
        try:
            room = self.server.rooms[room]
        except:
            return "Could not find {0}".format(room)
        return room

    # joins a room
    def join(self, array):
        rooms = self._search_rooms(array)
        rooms = self._room_action(rooms, 'add')
        retstring = "Joined "
        retstring += rooms
        return retstring

    def leave(self, array):
        rooms = self._search_rooms(array)
        rooms = self._room_action(rooms, 'remove', False)
        retstring = "Left "
        retstring += rooms
        return retstring

    def memberlist(self, keyB):
        room = self.findroom(keyB)
        if isinstance(room, str):
            return room

        memberstring = room.memberlist()
        if memberstring == "":
            return "No members in {0}".format(keyB)
        return memberstring

    def send(self, statusArray):

        if '-' not in statusArray:
            return ("Messages should be in the form: send [room] - [msg]. Please "
            "check formatting and try again.")
    
        index = statusArray.index('-')
        rooms = self._search_rooms(statusArray[:index])
        
        #remove index + 1 items of the status array and converts to a string
        msg = statusArray[index+1:]
        msg = ' '.join(msg)
        msg += '\n'
        for room in rooms:
            if isinstance(room, Room):
                room.sendall(self.name, msg)
        return ""

    def tell(self, statusArray):
        '''Sends a private message'''
        # if '-' not in statusArray:
        #     return ("Messages should be in the form: tell [name] - [msg]. Please "
        #     "check formatting and try again.")
        
        # dest will be 2nd option in the status array
        dest = statusArray[1]
        msg = statusArray[2:]
        msg = ' '.join(msg)
        msg += '\n'
        for thread in self.server.clients:
            if thread.name == dest:
                conn = thread.conn
                conn.send("{0} whispers to you : {1}".format(self.name, msg).encode("utf-8"))
                self.conn.send("You tell {0} : {1}".format(dest, msg).encode("utf-8"))
                return ""
        return "I'm sorry, it appears {0} is offline.".format(dest)



    def disconnect(self):
        for room in self.server.rooms:
            current = self.server.rooms[room]
            current.remove(self.name)
        self.conn.close()
        sys.exit(0)

    def _search_rooms(self, array):
        '''Searches an array of string for room names and
        returns any matches in the beginning of the array.'''
        res = []
        # Search the string for rooms
        for word in array[1:]:
            if self.findroom(word):
                res.append(self.findroom(word))
            else:
                break
        return res

    def _room_action(self, array, string, conn = True):
        '''Performs a method on the room class based on parameters given'''
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
                retstring += "{0}; ".format(' '.join(room.name for room in retrooms))
        if len(retrooms) < len(array):
            retstring += str(notfound)
        return retstring