import sim

n1=sim.Node("n1")
n2=sim.Node("n2")
n1.sendmsg(n2,"m:hi!")
n2.multicast("m:hihi!")
n1.sendmsg(n2,"ping:hi")
sim.local.actall()
