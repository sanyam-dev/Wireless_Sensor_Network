from network import network
import numpy as np

net = network(500, 500, 400, 0, 0)
path = "results/network_data/network1network_data.npy"
# path = "results/result16/9-graph_data.npy"
# path = "results/result93/3-graph_data.npy"
parent_dir = "./results/conventional/result"
# path = parent_dir + '/0-graph_data.npy'

gd = net.load_network(path, 1)
for Node in net.node_list:
	Node.critical_energy = 0.0
net.packet_length = 8

dead_node = set()
n = net.number_of_nodes
k = net.packet_length
sink = net.sink
rnd = 0
net.show_graph()
s_trans =0
net.calculate_latency()
lm = net.latency_matrix
energy_per_round = []
latency_per_round = []
throughput_per_round = []
total_latency=0
rnd_latency=0
er = sink.energy_for_reception(k)

while len(dead_node) < 0.9 * n:

	message_generated = n - len(dead_node)
	s_trans=0
	rnd_latency=0
	e=0
	for Node in net.node_list:
		d = sink.dist(Node)
		et = Node.energy_for_transmission(k,d)
		if et <= Node.current_energy:
			s_trans += 1
			rnd_latency += lm[Node.id][sink.id]
			Node.current_energy -= et
			e+=Node.current_energy
		else:
			dead_node.add(Node)

	latency_per_round.append(rnd_latency)
	throughput_per_round.append([message_generated, s_trans, 0, round(s_trans/message_generated, 2)])
	energy_per_round.append(e)
	total_latency += rnd_latency
	rnd += 1
	e=0
	s_trans =0
	message_generated = 0
	rnd_latency = 0

	for Node in net.node_list:
		if not Node.is_functional():
			dead_node.append(Node)



print("rounds : ", rnd)
avg_latency= total_latency/rnd

print("Average latency : ",avg_latency)
print("Throughput :", message_generated)

print("Total Energy Consumed : ",e)

net.save_network_performance(parent_dir + '/direct/', "direct-fl", rnd, energy_per_round, throughput_per_round, latency_per_round)