#!/usr/bin/python
import socket

host=''
port=91234

sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host,port))
while 1:
    data,addr = sock.recvfrom(1024)
    if not data: break
    print "data: %s"%data
    #conn.send(data)
sock.close()
