#!/usr/bin/python
from time import time,sleep
from random import shuffle
from socket import *
import struct
MYGROUP = '225.0.0.250'

def openmsendsocket():
	self.msendsocket=socket(AF_INET, SOCK_DGRAM)
	ttl = struct.pack('b', 1)
	self.msendsocket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
	
def openucastsocket(port):
	s = socket(AF_INET, SOCK_DGRAM)
	s.setblocking(0)
	s.bind(("",port))
	return s
def openmcastsocket(group, port):
    # Import modules used only here
    import string
    import struct

    s = socket(AF_INET, SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (not strictly needed)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    s.bind(('', port))

    # Look up multicast group address in name server
    # (doesn't hurt if it is already in ddd.ddd.ddd.ddd format)
    group = gethostbyname(group)

    # Construct binary group address
    bytes = map(int, string.split(group, "."))
    grpaddr = 0
    for byte in bytes: grpaddr = (grpaddr << 8) | byte

    # Construct struct mreq from grpaddr and ifaddr
    ifaddr = INADDR_ANY
    mreq = struct.pack('ll', htonl(grpaddr), htonl(ifaddr))
 
    # Add group membership
    s.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
 
    s.setblocking(0)
    return s

msendsocket=openmsendsocket()
def multicast(msg):
	msendsocket.sendto(msg, (MYGROUP, 81234))

def getslot(record):
	parts=record.split(".")
	domain="%s.%s"%(parts[-2],parts[-1])
	#print "DEBUG: domain: %s"%domain
	import hashlib
	hasher = hashlib.sha1()
	hasher.update(domain)
	hash=hasher.hexdigest()
	#print "DEBUG: hash: %s"%hash
	slot=hash[:2]
	#print "DEBUG: slot: %s"%slot
	return slot

class Node:
	def __init__(self,uid):
		self.guid=uid
		self.guid=getfqdn()
		self.msgqueue=[]
		self.rcvhistory=[]
		self.records={}
		self.groups=[]
		self.groupmembers={}
		self.addressmap={}
		self.mrecvsocket = openmcastsocket("225.0.0.250", 81234)
		self.urecvsocket = openucastsocket(91234)
		self.usendsocket = socket(AF_INET, SOCK_DGRAM)
		self.online=True
		self.hostlist={}
		self.dirtylist=False
		self.state="starting"
		self.ismaster=False
		self.lasttime=time()
		self.reqlist=[]
	def assignmaps(self):
		for n in xrange(16**2):
			val=hex(n)[2:]
			if val not in self.addressmap:
				self.addressmap[val]=[]

	def recvmsg(self,sendernode,msg):
		if self.online:
			self.msgqueue.append([msg,sendernode])
	def sendmsg(self,targetnode,msg):
		if self.online:
			self.usendsocket.sendto(msg,(targetnode,91234))
	def multicast(self,msg):
		multicast(msg)
	def sendlist(self):
		str="list:"
		for host in self.hostlist:
			str+="%s,%s\n"%(host,self.hostlist[host])
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
	def lookupw(self):
		slot = self.reqlist[0][0]
		record = self.reqlist[0][1]
		type = self.reqlist[0][2]
		#TODO: check to see if theres a lookup in progress, if it has succeeded, timed out, or is still in progress
		if slot in self.addressmap:
			#TODO: query the hosts in a random order
			l=self.addressmap[slot]
			shuffle(l)
			for h in l:
				sendmsg(h,"lookup:%s:A")
			self.lasttime=time()
			self.lastquad=self.reqlist[0]
			while time()<ctime+60:
				if not (slot,record,type) == (self.reqlist[0][0],self.reqlist[0][1],self.reqlist[0][2]):
					return
				sleep(.1)
			print "failed"
			#TODO: implement fallback lookup
				
	def lookup(self, type, record):
		if record in self.records:
			return self.records[record]
		else:
			slot=getslot(record)
			self.joingroup(slot)
			request=(slot,record,type,time())
			self.reqlist.append(request)
			while True:
				if not request in self.reqlist:
					return self.records[record]
				sleep(.1)
				#TODO:timeout

	def joingroup(self, group):
		if group not in self.groups:
			self.multicast("joingroup:%s"%group)
			self.groups.append(group)
			self.groupmembers[group]=[]
	def fillqueue(self):
		try:
			while True:
				data, sender = self.mrecvsocket.recvfrom(1500)
				while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
				self.recvmsg(sender[0],data)
		except error:
			pass
		try:
			while True:
				data, sender = self.urecvsocket.recvfrom(1024)
				while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
				self.recvmsg(sender[0],data)
		except error:
			pass
	def act(self):
		if self.online:
			try:
				self.fillqueue()
				msg=self.msgqueue.pop(0)
				text=msg[0]
				try:
					sender=msg[1].guid
				except AttributeError:
					sender=msg[1]
				self.rcvhistory.append(msg)
				try:
					print "%s got a msg from %s: %s"%(self.guid,sender,text)
				except AttributeError:
					print "%s got an anon msg: %s"%(self.guid,text)
				firstpart=text.split(":")[0]
				if firstpart=="m":
					print "===== %s says %s ====="%(sender,text.split(":")[1])
				elif firstpart=="ping":
					self.sendmsg(sender,"pong:%s"%text.split(":")[1])
				elif firstpart=="join":
					if self.ismaster:
						secondpart=text.split(":")[1]
						if secondpart not in self.hostlist:
							self.hostlist[secondpart]=sender
						self.dirtylist = True
				elif firstpart=="complain":
					if self.ismaster:
						secondpart=text.split(":")[1]
						if secondpart not in self.hostlist:
							self.hostlist[secondpart]=sender
						self.dirtylist = True
				elif firstpart=="list":
					newlistpairs=text.split(":")[1].split("\n")[:-1]
					newlist={}
					for pair in newlistpairs:
						newlist[pair.split(",")[0]]=pair.split(",")[1]
					if self.guid in newlist:
						self.hostlist=newlist
						if self.state=="joining":
							self.state="joined"
					else:
						self.multicast("complain:%s"%self.guid)
				elif firstpart=="dig":
					hname = text.split(":")[1]
					print "records:",self.records
					if hname in self.records:
						print "sending answer to %s"%msg[1]
						self.sendmsg(msg[1],"ans:%s:%s"%(hname,self.records[hname]))
				elif firstpart=="ans":
					hname = text.split(":")[1]
					result = text.split(":")[2]
					type = text.split(":")[3]
					if not hname in self.records:
						self.records[hname]=result
					for quad in self.reqlist:
						if quad[1]==hname and quad[2]==type:
							self.reqlist.remove(quad)
				elif firstpart=="joingroup":
					group = text.split(":")[1]
					if group in self.groups:
						self.sendmsg(sender,"member:%s:%s"%(group,self.guid))
						self.groupmembers[group].append(sender)

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
				if len(self.reqlist)>0:
					self.lookupw()
				return False
			return True
		return False
