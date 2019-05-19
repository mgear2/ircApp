class Room:
    def __init__(self, name, roomno):
        self.name = name
        self.id = roomno
        self.members = {}

    def add(self, name, conn):
        if name in self.members:
            return
        self.members[name] = conn
        return
        
    def remove(self, name):
        self.members.pop(name)
        return
    
    def memberlist(self):
        memberstring = ""
        for member in self.members:
            memberstring += (member + "\n")
        return memberstring

    def sendall(self, message): 
        for member in self.members: 
            conn = self.members[member] 
            conn.sendall(message.encode("utf-8"))
