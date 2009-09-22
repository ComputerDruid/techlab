#!/usr/bin/python
class Node:
	def __init__(self,uid):
		self.guid=uid
		self.msgqueue=[]
	def recvmsg(self,sendernode,msg):
		self.msgqueue.append([msg,sendernode.guid])
	def sendmsg(self,targetnode,msg):
		targetnode.recvmsg(self,msg)
	def act(self):
		try:
			msg=self.msgqueue.remove(0)
			print "#%s got a msg from %s: %s"%(self.guid,msg[1],msg[0])
		except ValueError:
			return
		
