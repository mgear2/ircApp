class Room:
    def __init__(self, name, roomno):
        self.name = name
        self.id = roomno
        self.members = {}

    def add(self, name, conn):
        if name in self.members:
            return
        self.members[name] = conn

    def remove(self, name):
        if name not in self.members:
            return
        self.members.pop(name)

    def memberlist(self):
        memberstring = ""
        for member in self.members:
            memberstring += (member + "\n")
        return memberstring

    def sendall(self, user, string):
        for member in self.members:
            conn = self.members[member]
            print("Sending to {0}".format(conn))
            message = user + " says: " + string
            conn.sendall(message.encode("utf-8"))