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
