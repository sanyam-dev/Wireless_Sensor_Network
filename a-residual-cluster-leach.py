from network import network
from node import node
import random
import numpy as np



path = "results/network_data/network1network_data.npy"
# path = "results/result16/9-graph_data.npy"
# path = "results/result93/3-graph_data.npy"

net = network(500, 500, 400, 0, 0)
gd = net.load_network(path)
net.packet_length = 8

for x in net.node_list:
	x.critical_energy = 0
sink = net.sink

net.calculate_latency()
dm = net.calculate_dist()
lm = net.latency_matrix
k = net.packet_length
er = sink.energy_for_reception(k)
dead_node = set()
rnds = 0
total_latency = 0
energy_consumed = 0
s_trans = 0
p_gen = 0
rnd_latency = 0

n = net.number_of_nodes
prev_round_energy_consumed =0
energy_per_round = []
latency_per_round = []
throughput_per_round = []

failed_itr_per_node = {}
ch_msg = {}
ch = {}

#	setting distance from server in every node:
for Node in net.node_list:
	Node.dist(sink)
	Node.setup_for_leach()
	failed_itr_per_node[Node] = 0
	ch_msg[Node] = 0

#	LEACH specific parameters
P = 0.04
failed_iterations = 0
clusters = []

#Node advertisement & cluster head selection
cluster_count = 0
for Node in net.node_list:
	Node.role = 0
	Tn = P/(1 - P*(rnds % int(1/P)))
	response = random.uniform(0,1)
	if response < Tn:
		Node.role = 1
		Node.clusterID = cluster_count
		ch[cluster_count] = Node
		clusters.append([Node])
		cluster_count += 1

#cluster formation
for Node in net.node_list:
	if Node.role == 0:
		Node.dist_to_head = 1e9
		for iiii in range(cluster_count):
			head = ch[iiii]
			d = Node.dist(head)
			if Node.dist_to_head != min(Node.dist_to_head, d):
				Node.dist_to_head = d
				Node.clusterID = iiii
		try:
			clusters[Node.clusterID].append(Node)
		except IndexError:
			print("error ", len(clusters) , cluster_count, iiii)
			quit()



while len(dead_node) < 0.9*n:
	message_gen = n - len(dead_node)
	l = 0
	e = 0
	rnd_latency = 0
	ch_count = 0
	s_trans = 0

	for i in range(cluster_count):
		head = ch[i]
		ch_msg[head] = 1
		if head in dead_node:
			continue
		for k in range(len(clusters[i])):
			Node = clusters[i][k]
			if Node.role == 0:
				if Node in dead_node:
					continue
				et = Node.energy_for_transmission(k, dm[Node.id][head.id])
				Node.current_energy -= et
				head.current_energy -= er
				e += et + er
				l += lm[Node.id][head.id]
				ch_msg[head] += 1

		et = head.energy_for_transmission(k, dm[head.id][sink.id])
		while head.current_energy > head.critical_energy and ch_msg[head] != 0:
			head.current_energy -= et
			e += et + er
			l += lm[head.id][sink.id]
			s_trans += 1
			ch_msg[head] -= 1

	energy_per_round.append(e)
	latency_per_round.append(l)
	throughput_per_round.append([message_gen, s_trans, round(s_trans/message_gen, 3)])
	rnds += 1

	for Node in net.node_list:
		if Node.current_energy < Node.critical_energy or failed_itr_per_node[Node] > 5:
			dead_node.add(Node)

	for Node in dead_node:
		if Node.role == 1:
			cluster = clusters[Node.clusterID]
			# Node with max energy left becomes cluster head
			max_energy_left = -1e9
			node_id = -1
			for member in cluster:
				if member in dead_node:
					continue
				if max_energy_left != max(max_energy_left, member.current_energy):
					max_energy_left = member.current_energy
					node_id = member.id
			if node_id == -1:
				continue
			ch[Node.clusterID] = net.node_map[node_id]

	print(rnds, len(dead_node), round(e, 3), round(l,3), round(s_trans/message_gen, 3))


avg_en = round(sum(energy_per_round)/rnds,3)
avg_lat = round(sum(latency_per_round)/rnds,3)
t_p = [i[2] for i in throughput_per_round]
avg_throughput = round(sum(t_p)/rnds,3)

print("lifetime", rnds)
