from node import *
from network import *
import networkx as nx

net = network(500, 500, 400, 0, 0)
path = "results/network_data/network1network_data.npy"
# path = "results/result16/9-graph_data.npy"
# path = "results/result93/3-graph_data.npy"
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

K_clusters=100 #no of clusters
graph_data = load_network(path, 1)

cluster_labels = np.load("./leach-cluster-label.npy", allow_pickle=True).item()
cluster_labels = cluster_labels['data']


cluster_labels = net.show_cluster(cluster_labels, K_clusters, set())
clusters = [[] for _ in range(K_clusters)]
cluster_map = {}



for Node in net.node_list:
	clusters[cluster_labels[Node.id - 1]].append(Node)
	cluster_map[Node] = cluster_labels[Node.id - 1]

print(len(clusters[0]))

sink = net.sink
dead_node = set()
k = net.packet_length
# k = 1000000
rnds = 0
n = net.number_of_nodes
n_map = net.node_map

total_latency=0
energy_consumed=0
s_trans = 0		#	successful transactions
p_gen = 0
rnd_latency=0

net.calculate_latency()
dm = net.calculate_dist()
lm = net.latency_matrix
prev_round_energy_consumed = 0
energy_per_round = []
latency_per_round = []
throughput_per_round = []
er = sink.energy_for_reception(k)

failed_itr_per_node = {}
ch_msg = {}

for Node in net.node_list:
	failed_itr_per_node[Node] = 0
	ch_msg[Node] = 0

while len(dead_node) < 0.9*n:

	message_gen = n - len(dead_node)
	e = 0
	l = 0
	s_trans = 0
	fails=0
	ch_msg.clear()

	for i in range(K_clusters):
		cluster = clusters[i]
		ch_index = random.randint(0, len(cluster)-1)
		ch = cluster[ch_index]
		ch_msg[ch] = 0
		for Node in cluster:
			if Node == ch:
				continue
			et = Node.energy_for_transmission(k, dm[Node.id][ch.id])
			if et > Node.current_energy:
				fails += 1
				failed_itr_per_node[Node] += 1
			else:
				Node.current_energy -= et
				ch.current_energy -= er
				e += et + er
				l += lm[Node.id][ch.id]
				ch_msg[ch] += 1

		et = ch.energy_for_transmission(k, dm[ch.id][sink.id])
		while ch_msg[ch] != 0 and ch.current_energy>ch.critical_energy:
			e += et + er
			l += lm[ch.id][sink.id]
			ch_msg[ch] -= 1
			ch.current_energy -= et
			s_trans += 1

	energy_per_round.append(e)
	latency_per_round.append(l)
	throughput_per_round.append([message_gen, s_trans, round(s_trans/message_gen, 3)])

	for Node in net.node_list:
		if Node.current_energy < Node.critical_energy or failed_itr_per_node[Node]>5:
			dead_node.add(Node)
			try:
				clusters[cluster_map[Node]].remove(Node)
			except ValueError:
				continue

	rnds += 1
	# if(rnds%100==0):
	print(rnds, len(dead_node), e, l, round(s_trans/message_gen, 3),fails)

	if(e == 0 and l == 0):
		break
print(rnds)
net.save_network_performance("./results/performance/leach","cluster-leach.npy", rnds, energy_per_round, throughput_per_round, latency_per_round)
net.show_cluster(cluster_labels, K_clusters, dead_node)