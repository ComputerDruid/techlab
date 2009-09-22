#!/usr/bin/python

class Link:
	def __init__(self):
		self.nodes=[]
	def addnode(self,n):
		self.nodes.append(n)
	def multicast(self,sender,msg):
		for n in self.nodes:
			n.recvmsg(sender,msg)
	def actall(self):
		anything=True
		while anything:
			anything=False #pessimistic view
			for n in self.nodes:
				if n.act():
					anything=True

local = Link()

class Node:
	def __init__(self,uid,link=local):
		self.guid=uid
		self.msgqueue=[]
		self.online=True
		self.link=link
		self.link.addnode(self)
	def recvmsg(self,sendernode,msg):
		if self.online:
			self.msgqueue.append([msg,sendernode])
	def sendmsg(self,targetnode,msg):
		targetnode.recvmsg(self,msg)
	def multicast(self,msg):
		self.link.multicast(self,msg)
	def act(self):
		if self.online:
			try:
				msg=self.msgqueue.pop(0)
				print "#%s got a msg from %s: %s"%(self.guid,msg[1].guid,msg[0])
				if msg[0].split(":")[0]=="m":
					print "===== %s says %s ====="%(msg[1].guid,msg[0].split(":")[1])
				elif msg[0].split(":")[0]=="ping":
					self.sendmsg(msg[1],"pong:%s"%msg[0].split(":")[1])
			except IndexError:
				return False
			return True
		return False
