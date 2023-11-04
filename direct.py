from network import network
import numpy as np

net = network(500, 500, 400, 0, 0)
# path = "results/network_data/network1network_data.npy"
# path = "results/result16/9-graph_data.npy"
path = "results/result93/3-graph_data.npy"
def load_network(graph_data_path, save_mode):
	"""
	save_mode: 0 -> old network data
	save_mode: 1 -> new network data
	"""
	if(save_mode == 0):
		net.initialise_nodes_fixed(1, 0)
		net.set_parameters(2000, 8, 2000, 3*1e8, 50)
		#load graph
		graph_data = np.load(graph_data_path, allow_pickle=True).item()
		net.set_nxg_from_npy(graph_data)
	else:
		_, _, graph_data = net.load_network_topology(graph_data_path)
		net.set_nxg_from_npy(graph_data)
		net.packet_length = 8

	for Node in net.node_list:
		Node.critical_energy = 0.0

	return graph_data

gd = load_network(path,0)
energy_consumed=0

dead_node = set()
n = net.number_of_nodes
k = net.packet_length
sink = net.sink
rnd = 0
net.show_graph()
s_trans =0
net.calculate_latency()
lm = net.latency_matrix
prev_round_energy_consumed = 0
energy_per_round = []
latency_per_round = []
throughput_per_round = []
total_latency=0
rnd_latency=0
er = sink.energy_for_reception(k)

while len(dead_node) < 0.9 * n:

	message_generated = n - len(dead_node)
	for Node in net.node_list:
		d = sink.dist(Node)
		et = Node.energy_for_transmission(k,d)
		if et <= Node.current_energy:
			s_trans += 1
			rnd_latency += lm[Node.id][sink.id]
			energy_consumed += et + er
			Node.current_energy -= et
		else:
			dead_node.add(Node)

	latency_per_round.append(rnd_latency)
	throughput_per_round.append([message_generated, s_trans, 0, round(s_trans/message_generated, 2)])
	energy_per_round.append(energy_consumed - prev_round_energy_consumed)
	prev_round_energy_consumed = energy_consumed
	total_latency += rnd_latency
	rnd += 1
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

print("Total Energy Consumed : ",energy_consumed)
path = "results/performance/direct/"
net.save_network_performance(path, "res-server", rnd, energy_per_round, throughput_per_round, latency_per_round)