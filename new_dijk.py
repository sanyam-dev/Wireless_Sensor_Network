from node import *
from network import *

net = network(500, 500, 400, 0, 0)
net.set_parameters(2000, 200, 2000, 2000, 50)
net.initialise_nodes_fixed(1, 0.4)
sink = net.sink
# net.show_network()
# net.get_graph()
# print(net.get_acc())
dead_node = set()
k = net.packet_length
rnds = 0
n = net.number_of_nodes
n_map = net.node_map

total_latency=0

s_trans = 0		#	successful transactions
p_gen = 0	#	messages generated

while len(dead_node) < 0.9*n:
	rnd_latency=0
	total_latency+=rnd_latency
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
			curr.current_energy -= curr.energy_for_transmission(k, next.dist(curr))
			next.current_energy -= next.energy_for_reception(k)
			rnd_latency+=(net.latency(curr,next))
			curr = next

		
		if curr.id == 0:
			s_trans += 1
		elif curr.current_energy > curr.energy_for_transmission(k, curr.dist(net.sink)):
			curr.current_energy -= curr.energy_for_transmission(k, curr.dist(net.sink))
			rnd_latency+=(net.latency(curr,sink))
			s_trans += 1
		elif curr.id == i:
			dead_node.add(i)
		

	rnds += 1
	print("----")
	print(rnds, len(dead_node))
	print("----")
print(s_trans, p_gen, s_trans/p_gen)

total_latency+=rnd_latency

avg_latency= total_latency/rnds

print("Average latency : ",avg_latency)

