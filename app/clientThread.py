from threading import Thread

class clientThread(Thread):
    def __init__(self, Server, conn, addr):
        super(clientThread, self).__init__()
        self.name = addr
        self.conn = conn
        self.server = Server

    # thread created will run this method to facilitate communication between the client and the server
    def run(self):
        self.conn.send("Welcome. Connection info: {0}".format(self.conn).encode("utf-8"))
        while True: 
            data = self.conn.recv(1000000)
            print(data)
            if data.decode("utf-8") == "exit":
                break
            reply = self.verify(data.decode("utf-8"))
            print("Sending: " + reply)
            self.conn.sendall(reply.encode("utf-8"))
        self.conn.close()

    def verify(self, data):
        statusArray = data.split()
        keyA = statusArray[0]
        if len(statusArray) > 1:
            keyB = statusArray[1]
        else:
            keyB = "Default"

        reply = "Verified"

        if keyA == "new":
            reply = self.new(keyB)
        elif keyA == "kill":
            reply = self.kill()
        elif keyA == "clients":
            reply = self.clients()
        elif keyA == "rooms":
            reply = self.rooms()
        elif keyA == "join":
            reply = self.join(keyB)
        elif keyA == "leave":
            reply = self.leave(keyB)
        elif keyA == "members":
            reply = self.memberlist(keyB)
        elif keyA == "send":
            reply = self.send(keyB, statusArray)

        return reply

    def new(self, keyB):
        # room creation
        returnval = self.server.newroom(keyB)
        if not returnval:
            return "Roomname {0} in use!".format(keyB)
        return "Creating new room: {0}".format(keyB)

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
    def join(self, keyB):
        room = self.findroom(keyB)
        if isinstance(room, str):
            return room

        room.add(self.name, self.conn)

        return "Joined {0}".format(keyB)

    def leave(self, keyB):
        room = self.findroom(keyB)
        if isinstance(room, str):
            return room

        room.remove(self.name)

        return "Left {0}".format(keyB)

    def memberlist(self, keyB):
        room = self.findroom(keyB)
        if isinstance(room, str):
            return room

        memberstring = room.memberlist()
        if memberstring == "":
            return "No members in {0}".format(keyB)
        return memberstring

    def send(self, keyB, statusArray):
        room = self.findroom(keyB)
        if isinstance(room, str):
            return room

        room.sendall(str(statusArray))
        return " Received"