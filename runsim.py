#!/usr/bin/python
import sim
from time import sleep
def step():
	sim.local.actall()
	sleep(1)
n1=sim.Node("n1")
n2=sim.Node("n2")
n1.sendmsg(n2,"m:hi!")
step()
n2.multicast("m:hihi!")
step()
n1.sendmsg(n2,"ping:hi")
step()
n1.ismaster=True
n3=sim.Node("n3")
step()
list=[0]*10
for n in xrange(10):
	list[n]=sim.Node("node%d"%n)
step()
#while True:
#	line=raw_input()
#	try:
#		exec(line)
#	except:
#		print "Error"

