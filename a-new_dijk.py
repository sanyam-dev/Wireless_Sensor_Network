from node import *
from network import *

# net = network(500, 500, 400, 0, 0)
# net.initialise_nodes_fixed(1, 0.4)
# net.set_parameters(2000, 200, 2000, 3*1e8, 50)
# net.set_nxg()

net = network(500, 500, 400, 0, 0)
# path = "results/network_data/network1network_data.npy"
# path = "results/result93/3-graph_data.npy"
path = "results/result16/9-graph_data.npy"

gd = net.load_network(path)
for Node in net.node_list:
	Node.critical_energy = 0.0
net.packet_length = 8
sink = net.sink
dead_node = set()
k = net.packet_length
rnds = 0
n = net.number_of_nodes
n_map = net.node_map

total_latency=0
energy_consumed=0
s_trans = 0		#	successful transactions
p_gen = 0
rnd_latency=0

net.calculate_latency()
lm = net.latency_matrix
prev_round_energy_consumed = 0
energy_per_round = []
latency_per_round = []
throughput_per_round = []

while len(dead_node) < 0.9*n:

	message_generated = n - len(dead_node)
	p_gen = 0
	for Node in net.node_list:
		if Node in dead_node:
			continue
		p_gen += 1
		curr = Node
		path = net.findShortestPath(curr)
		# print(i, path)
		while len(path) != 0:
			next = net.node_map[path.pop()]
			# rnd_latency+=(net.latency(curr,next))
			rnd_latency += lm[curr.id][next.id]
			trns=curr.energy_for_transmission(k, next.dist(curr))
			curr.current_energy -= trns
			recep=next.energy_for_reception(k)
			next.current_energy -= recep
			energy_consumed+=recep
			curr = next

		snk=curr.energy_for_transmission(k, curr.dist(net.sink))
		if curr.current_energy > snk:
			curr.current_energy -= snk
			rnd_latency += lm[curr.id][sink.id]
			energy_consumed += snk
			s_trans += 1
		elif curr == Node:
			dead_node.add(Node)

	print("----")
	latency_per_round.append(rnd_latency)
	throughput_per_round.append([message_generated, s_trans, p_gen, round(s_trans/message_generated, 2)])
	energy_per_round.append(energy_consumed - prev_round_energy_consumed)
	prev_round_energy_consumed = energy_consumed
	total_latency+=rnd_latency
	rnd_latency=0
	rnds += 1
	for Node in net.node_list:
		if Node.current_energy < Node.critical_energy:
			dead_node.add(Node)

	print(rnds, len(dead_node))
	print("----")

total_latency+=rnd_latency

avg_latency= total_latency/rnds
print(rnds)

print("Average latency : ",avg_latency)
print("Throughput : ",s_trans/message_generated, message_generated, p_gen)
print("Total Energy Consumed : ",energy_consumed)

net.save_network_performance("results/performance","result16-8-11",rnds,energy_per_round,throughput_per_round,latency_per_round)