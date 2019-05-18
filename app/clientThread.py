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

        return reply

    def new(self, statusArray):
        # room creation
        if len(statusArray) > 1:
            keyB = statusArray[1]
        else:
            keyB = "Default"

        self.server.newroom(keyB)
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