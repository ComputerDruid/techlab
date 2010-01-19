#!/usr/bin/python
import socket

host='localhost'
#port=9001
port=91234

sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while 1:
    msg=raw_input()
    sock.sendto(msg,(host,port))
sock.close()
