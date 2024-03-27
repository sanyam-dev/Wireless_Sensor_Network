from network import *
from networkx import NetworkXError

net = network(500, 500, 400, 0, 0)
path = "results/network_data/network1network_data.npy"
# path = "results/result93/3-graph_data.npy"
# path = "results/result16/9-graph_data.npy"
parent_dir = "results/conventional/result"
# path = parent_dir + "/0-graph_data.npy"

gd = net.load_network(path, 1)
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
	message_gen = n - len(dead_node)
	s_trans = 0
	e = 0
	l = 0
	failed_msg = 0
	for node in net.node_list:
		if node in dead_node:
			continue
		path = nx.shortest_path(net.nxg, 0, node.id)
		path.reverse()
		curr = net.node_map[path.pop()]
		fail = 0
		while len(path) != 0:
			next = net.node_map[path.pop()]
			if next.current_energy < next.critical_energy or curr.current_energy < curr.critical_energy:
				fail = 1
				break
			l += lm[curr.id][next.id]
			curr.current_energy -= curr.energy_for_transmission(k, next.dist(curr))
			next.current_energy -= er
			curr = next
		if curr != sink or fail == 1:
			et = node.energy_for_transmission(k, dm[node.id][sink.id])
			if et > node.current_energy:
				failed_msg += 1
				dead_node.add(node)
				try:
					net.nxg.remove_node(node)
				except NetworkXError:
					print(node.id)
			else:
				node.current_energy -= et
				s_trans += 1
				continue
	for node in net.node_list:
		e += max(node.current_energy, node.critical_energy)
		if node.current_energy <= node.critical_energy:
			dead_node.add(node)

	latency_per_round.append(l)
	energy_per_round.append(e)
	throughput_per_round.append([message_gen, s_trans, s_trans/message_gen, failed_msg])
	total_latency+= l
	e = 0
	l = 0
	s_trans = 0
	failed_msg=0
	rnds += 1

total_latency+= l

avg_latency= total_latency/rnds
print(rnds)

total_latency+= l

avg_latency= total_latency/rnds
print(rnds)

print("Average latency : ",avg_latency)
print("Throughput : ",s_trans/message_gen)
net.save_network_performance(parent_dir + "/multi-hop","fl",rnds,energy_per_round,throughput_per_round,latency_per_round)