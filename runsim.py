#!/usr/bin/python
import sim
import os
import threading
from time import sleep

msgbuffer=[]
bufferlock=threading.Lock()
doquit=False
def run():
	mybuffer=[]
	while True:
		if len(mybuffer)==0:
			try:
				bufferlock.acquire()
				while len(msgbuffer)>0:
					mybuffer.append(msgbuffer.pop(0))
			finally:
				bufferlock.release()
		if len(mybuffer)>0:
			msg=mybuffer.pop(0)
			print "typed:%s"%msg
			if msg=="list":
				print "ismaster:%s"%n1.ismaster
				print "hostlist:%s"%n1.hostlist
				print "records:%s"%n1.records
			elif "," in msg:
				parts=msg.split(",")
				if parts[0]=="lookup":
					print "lookup:%s"%n1.lookup("a",parts[1])
			else:
				n1.multicast("m:%s"%msg)
		n1.act()
		if doquit:
			return
		sleep(.1)

n1=sim.Node(os.uname()[1])
procthread=threading.Thread(name="processing", target=run)
procthread.start()
while True:
	str=""
	try:
		str=raw_input()
	except EOFError:
		doquit=True
		break
	try:
		bufferlock.acquire()
		msgbuffer.append(str)
	finally:
		bufferlock.release()
