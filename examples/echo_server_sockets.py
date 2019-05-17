#!/usr/bin/python
# USAGE:   echo_server_sockets.py <PORT>
#
# EXAMPLE: echo_server_sockets.py 8000
import socket
import sys

if len(sys.argv) < 2:
    print ("USAGE:   echo_server_sockets.py <PORT>")
    sys.exit(0)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = ''
port = int(sys.argv[1])
s.bind((host, port))
s.listen(1)
while (1):
    conn, addr = s.accept()
    print ('client is at', addr)
    data = conn.recv(1000000)
    updata = data
    print ('sending data ', updata)
    conn.send(updata)
    conn.close()
    