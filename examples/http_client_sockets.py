#!/usr/bin/python
# Simple Python function that issues an HTTP request
# USAGE:   http_client_sockets.py <HOSTNAME> <PATH>
#           
# EXAMPLE: http_client_sockets.py www.google.com /
#
import sys
from socket import socket, gethostbyname, AF_INET, SOCK_STREAM

def http_req(server, path):

    # Creating a socket to connect and read from
    s=socket(AF_INET,SOCK_STREAM)

    # Finding server address (assuming port 8000)
    adr=(gethostbyname(server),8000)

    # Connecting to server
    s.connect(adr)

    # Sending request
    getString = "GET "+path+" HTTP/1.0\n\n"
    s.sendall(getString.encode('utf-8'))

    # Printing response
    resp=s.recv(1024)
    while resp!="":
	    print (resp)
	    resp=s.recv(1024)

http_req(sys.argv[1],sys.argv[2])
