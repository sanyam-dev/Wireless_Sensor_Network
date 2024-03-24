from network import network
import random
import numpy as np

net = network(500, 500, 400, 0, 0)
path = "results/network_data/network1network_data.npy"
# path = "results/result16/9-graph_data.npy"
# path = "results/result93/3-graph_data.npy"
graph_data = net.load_network(path,1)
net.packet_length = 8
for Node in net.node_list:
	Node.critical_energy = 0

sink = net.sink
dead_node = set()
k = net.packet_length
rnds = 0
n = net.number_of_nodes
n_map = net.node_map

s_trans = 0		#	successful transactions
p_gen = 0

net.calculate_latency()
dm = net.calculate_dist()
lm = net.latency_matrix
energy_per_round = []
latency_per_round = []
throughput_per_round = []
er = sink.energy_for_reception(k)

failed_itr_per_node = {}
ch_msg = {}
ch = {}
clusters_count = 0

#	setting distance from server in every node:
for Node in net.node_list:
	Node.dist(sink)
	Node.setup_for_leach()
	failed_itr_per_node[Node] = 0
	ch_msg[Node] = 0

#	LEACH specific parameters
P = 0.3
failed_iterations = 0
clusters = []


#Node advertisement & cluster head selection
for Node in net.node_list:
	Node.role = 0
	Tn = P/(1 - P*(rnds % int(1/P)))
	response = random.uniform(0,1)
	if response < Tn:
		Node.role = 1
		Node.clusterID = clusters_count
		clusters.append({Node})
		ch[clusters_count] = Node
		clusters_count += 1


#cluster formation
for Node in net.node_list:
	if Node.role == 0:
		Node.dist_to_head = 1e9

		for i in range(clusters_count):
			head = ch[i]
			d = Node.dist(head)
			if Node.dist_to_head != min(Node.dist_to_head, d):
				Node.dist_to_head = d
				Node.clusterID = i

		# if Node.dist_to_head <= net.radio_distance:
		clusters[Node.clusterID].add(Node)
		# else:
		# 	dead_node.add(Node)

nodes_not_participating = len(dead_node)
print(nodes_not_participating, len(net.node_list))
#	main loop


while len(dead_node) < 0.9*net.number_of_nodes:

	message_gen = net.number_of_nodes - len(dead_node)
	l =0
	e_residual = 0
	s_trans = 0

	for i in range(clusters_count):
		head = ch[i]
		for member in clusters[i]:
			if member.role == 0 and member not in dead_node:
				et = member.energy_for_transmission(k, dm[member.id][head.id])
				member.current_energy -= et
				head.current_energy -= er
				l += lm[member.id][head.id]
				ch_msg[head] += 1

		et = head.energy_for_transmission(k, dm[head.id][sink.id])
		head_available_energy = head.current_energy - head.critical_energy
		number_of_transmittable_message = head_available_energy // et
		head_message_transmitted = min(number_of_transmittable_message, ch_msg[head])
		head.current_energy -= (head_message_transmitted * et)
		l += (lm[head.id][sink.id] * head_message_transmitted)
		ch_msg[head] = 0
		s_trans += head_message_transmitted

		#since we are not re-electing heads in this method
		if head.current_energy < et:
			
			dead_node.add(head)



	#if cluster head is dead, the whole cluster dies
	#therefore, we pop the cluster & put the enti
	dead_clusters = []
	for i in range(clusters_count):
		head = ch[i]
		if head in dead_node:
			dead_clusters.append(clusters[i])
			for member in clusters[i]:
				dead_node.add(member)

	for dead_cluster in dead_clusters:
		clusters.remove(dead_cluster)

	clusters_count -= len(dead_clusters)

	for Node in net.node_list:
		e_residual += max(Node.current_energy, Node.critical_energy)
		if Node.current_energy < Node.critical_energy or failed_itr_per_node[Node] > 1:
			dead_node.add(Node)

	energy_per_round.append(e_residual)
	latency_per_round.append(l)
	throughput_per_round.append([message_gen, s_trans, round(s_trans/message_gen, 3)])
	if round(s_trans/message_gen, 3) > 1:
		fake = "YES"
	else:
		fake = "NO"
	print(rnds, net.number_of_nodes - len(dead_node), e_residual, l, round(s_trans/message_gen, 3), fake )
	rnds += 1
	message_gen = 0
	s_trans = 0
	l = 0
	e_residual = 0


save_path = "results/performance/leach/P-" + str(P) + "/"
net.save_network_performance(save_path, str(100), rnds, energy_per_round, throughput_per_round, latency_per_round)
print("lifetime", rnds, nodes_not_participating)