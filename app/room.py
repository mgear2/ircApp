class Room:
    """ Contains information about chat rooms.

    Args:
        name (str) : the name of the room.
        roomno (int) : A unique integer room identifier.
    
    Attributes:
        name (str) : the name of the room.
        roomno (int) : A unique integer room identifier.
        members (dict) : A dictionary that holds connection information for 
            members of room.
    
    """

    def __init__(self, name, roomno):
        self.name = name
        self.id = roomno
        self.members = {}

    def add(self, name, conn):
        """ Adds client information to room's member attribute.

        Args:
            name (str) : client user name
            conn (Socket) : client connection information.

        """

        if name in self.members:
            return
        self.members[name] = conn
        return

    def remove(self, name):
        """ Removes client from room's member attribute.

        Args:
            name (str) : client's user name.
        
        """

        if name not in self.members:
            return
        self.members.pop(name)
        return 

    def memberlist(self):
        """ Creates a list of members.

        Returns:
            str: string containing user names of all client's in room.
        
        """

        memberstring = ""
        for member in self.members:
            memberstring += (member + "\n")
        return memberstring

    def sendall(self, user, string):
        """ Sends messages to all users in room.

        Args:
            user (str) : User name of sender.
            string (str) : Message to be sent.
        
        """
        
        for member in self.members:
            conn = self.members[member]
            print("Sending to {0}".format(conn))
            message = user + " says in room " + self.name + " : " + string
            conn.sendall(message.encode("utf-8"))
        return 