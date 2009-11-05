#!/usr/bin/python
from time import time

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
		self.rcvhistory=[]
		self.records={}
		self.online=True
		self.link=link
		self.link.addnode(self)
		self.hostlist=[self.guid]
		self.dirtylist=False
		self.state="starting"
		self.ismaster=False
		self.lasttime=time()
	def recvmsg(self,sendernode,msg):
		if self.online:
			self.msgqueue.append([msg,sendernode])
	def sendmsg(self,targetnode,msg):
		targetnode.recvmsg(self,msg)
	def multicast(self,msg):
		self.link.multicast(self,msg)
	def sendlist(self):
		str="list:"
		for host in self.hostlist:
			str+="%s\n"%host
		self.multicast(str)
	def rebalance(self):
		print "delegation:"
		deleg=[0]*(len(hostlist)+1)
		for n in xrange(len(hostlist)):
			deleg[n]=[]
			temppos=n
			while temppos < LENSPACE:
				deleg[n].append(temppos)
				temppos+=LENSPACE/len(hostlist)
			print "%s:%s"%(hostlist[n],deleg[n])
	def lookup(self, type, record):
		if record in records:
			return records[record]
		else:
			self.multicast("dig:%s:%s"%(type,record))
	def act(self):
		if self.online:
			try:
				msg=self.msgqueue.pop(0)
				self.rcvhistory.append(msg)
				print "#%s got a msg from %s: %s"%(self.guid,msg[1].guid,msg[0])
				firstpart=msg[0].split(":")[0]
				if firstpart=="m":
					print "===== %s says %s ====="%(msg[1].guid,msg[0].split(":")[1])
				elif firstpart=="ping":
					self.sendmsg(msg[1],"pong:%s"%msg[0].split(":")[1])
				elif firstpart=="join":
					if self.ismaster:
						if msg[1].guid not in self.hostlist:
							self.hostlist.append(msg[1].guid)
							self.dirtylist = True
				elif firstpart=="complain":
					if self.ismaster:
						if msg[1].guid not in self.hostlist:
							self.hostlist.append(msg[1].guid)
							self.sendlist()
				elif firstpart=="list":
					newlist=msg[0].split(":")[1].split("\n")[:-1]
					if self.guid in newlist:
						list=newlist
						if self.state=="joining":
							self.state="joined"
					else:
						self.multicast("complain:%s"%self.guid)
				elif firstpart=="dig":
					hname = msg[0].split(":")[2]
					if hname in records:
						self.sendmsg(msg[1],"ans:%s"%records[hname])

			except IndexError:
				if self.state=="starting":
					self.multicast("join:%s"%self.guid)
					self.state="joining"
					self.lasttime=time()
					return True
				if self.state=="joining":
					curtime=time()
					if curtime-self.lasttime>5:
						print "%s: Taking Master"%self.guid
						self.lasttime=time()
						self.ismaster=True
						self.sendlist()
						self.state="joined"
					else:
						return True #keep going until you join
				if self.state=="joined":
					if self.ismaster:
						if self.dirtylist:
							self.sendlist()
							self.dirtylist=False
				return False
			return True
		return False
