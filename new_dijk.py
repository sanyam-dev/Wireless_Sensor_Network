from node import *
from network import *

net = network(500, 500, 400, 0, 0)
net.initialise_nodes_fixed(1, 0.4)
net.set_parameters(2000, 200, 2000, 3*1e8, 50)
net.set_nxg()
sink = net.sink
dead_node = set()
k = net.packet_length
rnds = 0
n = net.number_of_nodes
n_map = net.node_map

total_latency=0
energy_consumed=0
s_trans = 0		#	successful transactions
p_gen = 0	#	messages generated
rnd_latency=0
while len(dead_node) < 0.9*n:

	total_latency+=rnd_latency
	rnd_latency=0
	for i in range(1, n + 1):
		if i in dead_node:
			continue

		curr = n_map[i]
		if curr.current_energy < curr.critical_energy:
			dead_node.add(i)
			continue

		p_gen += 1
		path = net.findShortestPath(curr)

		# print(i, path)
		while len(path) != 0:

			next = net.node_map[path.pop()]
			rnd_latency+=(net.latency(curr,next))
			trns=curr.energy_for_transmission(k, next.dist(curr))
			curr.current_energy -= trns
			recep=next.energy_for_reception(k)
			next.current_energy -= recep
			energy_consumed+=recep
			curr = next

		snk=curr.energy_for_transmission(k, curr.dist(net.sink))
		if curr.id == 0:
			s_trans += 1
		elif curr.current_energy > snk:
			curr.current_energy -= snk
			rnd_latency+=(net.latency(curr,sink))
			energy_consumed+=snk
			s_trans += 1
		elif curr.id == i:
			dead_node.add(i)


	rnds += 1
	print("----")
	print(rnds, len(dead_node))
	print("----")

total_latency+=rnd_latency

avg_latency= total_latency/rnds
print(rnds)

print("Average latency : ",avg_latency)
print("Throughput : ",s_trans/p_gen)

print("Total Energy Consumed : ",energy_consumed)