from threading import Thread

class clientThread(Thread):
    def __init__(self, Server, conn, addr):
        super(clientThread, self).__init__()
        self.name = addr
        self.conn = conn
        self.server = Server
        self.memberlist = []

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
        
        keyB = 0
        if len(statusArray) > 1:
            keyB = statusArray[1]
        else:
            keyB = "Default"
        
        reply = "Verified"

        if keyA == "new":
            print("keyA == new")
            reply = self.new(statusArray)
        elif keyA == "kill":
            print("keyA == kill")
            reply = self.kill()
        elif keyA == "clients":
            print("keyA == clients")
            reply = self.clients()
        elif keyA == "rooms":
            print("keyA == rooms")
            reply = self.rooms()
        elif keyA == "join":
            print(f"keyB == {keyB}")
            reply = self.join(keyB)
        elif keyA == 'leave':
            reply = self.leave(keyB)
        elif keyA == 'members':
            reply = self.members(keyB)
        elif keyA == 'chat':
            reply = self.sendall(keyB, statusArray)

        return reply

    def new(self, statusArray):
        # room creation
        if len(statusArray) > 1:
            keyB = statusArray[1]
        else:
            keyB = "Default"

        res = self.server.newroom(keyB)
        if not res:
            return "Room in use, please enter new name.\n"
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

    def join(self, keyB):
        # joins a room
        try:
            room = self.server.rooms[keyB]
        except:
            return "Could not find room"
        room.add(self.name, self.conn)
        return "Joining room"

    def leave(self, keyB):
        #leaves a room
        try:
            room = self.server.rooms[keyB]
        except:
            return "Could not find room"
        room.remove(self.name)
        return "Joining room"

    def members(self, keyB):
        try:
            room = self.server.rooms[keyB]
        except:
            return "Coult not find room"
        string = room.memberlist()
        if string == "":
            string = "No members in room"
        return string

    def sendall(self, keyB, statusArray):
        try:
            room = self.server.rooms[keyB]
        except:
            return "Could not find room"
        msg = "".join(str(item + ' ') for item in statusArray[2:])
        msg += '\n'
        room.sendall(msg)
        return "Sending message..."
