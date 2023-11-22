from node import *
from network import *
import networkx as nx
# net = network(500, 500, 400, 0, 0)
# net.initialise_nodes_fixed(1, 0.4)
# net.set_parameters(2000, 200, 2000, 3*1e8, 50)
# net.set_nxg()

net = network(500, 500, 400, 0, 0)
# path = "results/network_data/network1network_data.npy"
path = "results/result93/3-graph_data.npy"
# path = "results/result16/9-graph_data.npy"

gd = net.load_network(path, 0)
e = 0
for Node in net.node_list:
	Node.critical_energy = 0.0
	e += Node.current_energy

net.packet_length = 8
sink = net.sink
dead_node = set()
k = net.packet_length
rnds = 0

er = sink.energy_for_reception(k)
n = net.number_of_nodes
n_map = net.node_map
net.calculate_latency()
lm = net.latency_matrix
dm = net.calculate_dist()
energy_per_round = [e]
latency_per_round = []
throughput_per_round = []
total_latency = 0
while len(dead_node) < 0.9*n:
	message_generated = n - len(dead_node)
	e = 0
	l = 0
	s_trans = 0

	for Node in net.node_list:
		if Node not in dead_node:
			path = nx.astar_path(net.nxg, 0, Node.id)
			path.reverse()
			curr = net.node_map[path.pop()]
			if len(path) == 0:
				et = Node.energy_for_transmission(k, dm[Node.id][sink.id])
				if et > Node.current_energy:
					dead_node.add(Node)
				else:
					Node.current_energy -= et
					s_trans += 1
					continue
			while len(path) != 0:
				next = net.node_map[path.pop()]
				l += lm[curr.id][next.id]
				curr.current_energy -= curr.energy_for_transmission(k, next.dist(curr))
				next.current_energy -= er
				curr = next

			s_trans += 1

	for Node in net.node_list:
		e += max(Node.current_energy, Node.critical_energy)
		if Node.current_energy <= Node.critical_energy:
			dead_node.add(Node)

	latency_per_round.append(l)
	energy_per_round.append(e)
	throughput_per_round.append([message_generated, s_trans, round(s_trans/message_generated, 3)])

	print("----")
	print(rnds, len(dead_node), e, round(l,3), round(s_trans/message_generated, 3))
	total_latency+= l
	e = 0
	l = 0
	s_trans = 0
	rnds += 1
	print("----")

total_latency+= l

avg_latency= total_latency/rnds
print(rnds)


save_path = "results/performance/multi-hop/a-star/sw"
net.save_network_performance(save_path, str(100), rnds, energy_per_round, throughput_per_round, latency_per_round)
print("lifetime", rnds)
