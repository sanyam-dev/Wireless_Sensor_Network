from network import network
import random
import numpy as np

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

K_clusters=40 #no of clusters
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

#	setting distance from server in every node:
for Node in net.node_list:
	Node.dist(sink)
	Node.setup_for_leach()
	failed_itr_per_node[Node] = 0
	ch_msg[Node] = 0

#	LEACH specific parameters
P = 0.025
not_cluster_heads = set(i for i in range(1, n + 1))
failed_iterations = 0

#	main loop
rnd_latency=0
while len(dead_node) < 0.9*net.number_of_nodes:
	message_gen = net.number_of_nodes - len(dead_node)
	l =0
	e = 0
	ch_count = 0
	for Node in net.node_list:
		Node.role = 0
		if Node in dead_node:
			continue
		Tn = 0
		
		if(rnds - Node.last_head_rnd > int(1/P)):
			Tn = P/(1 - P*(rnds % int(1/P)))
			# print("Tn", Tn)
			response = round(random.uniform(0,1), 3)
			if response < Tn:
				Node.role = 1
				try:
					clusters[ch_count].append(Node)
				except IndexError:
					clusters.append([Node])
				ch_count += 1

	print("ch_count", ch_count, message_gen)
	print("-----")
	for Node in net.node_list:
		if Node in dead_node:
			continue
		if Node.role == 0:
			Node.dist_to_head = 1e9
			for i in range(len(clusters)):
				head = clusters[i][0]
				if Node.dist_to_head > dm[Node.id][head.id]:
					Node.clusterID = i
					Node.dist_to_head = dm[Node.id][head.id]
			clusters[Node.clusterID].append(Node)

	for i in range(len(clusters)):
		head = clusters[i][0]
		for k in range(1, len(clusters[i])):
			Node = clusters[i][k]
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

	print(rnds, len(dead_node), round(e, 3), round(l,3), round(s_trans/message_gen, 3))




print("lifetime", rnds)










# 	#	each node transmit data once every round
# 	total_latency+=rnd_latency
# 	rnds += 1
# 	round_wise_cluster_head = []
# 	rnd_latency=0
# 	#	Advertising Phase
# 	for Node in net.node_list:

# 		Node.role = 0

# 		if Node.critical_energy > Node.current_energy:
# 			operational_nodes = operational_nodes - 1
# 			dead_node.append(Node)
# 			net.node_list.remove(Node)
# 			pass

# 		if(rnds - Node.last_head_rnd > int(1/P)):
# 			not_cluster_heads.add(Node.id)

# 		Tn = 0

# 		if Node.id in not_cluster_heads:
# 			Tn = P/(1 - P*(rnds % int(1/P)))

# 		response = round(random.uniform(0,1), 3)
# 		if response < Tn:
# 			Node.role = 1
# 			Node.times_elected += 1
# 			Node.last_head_rnd = rnds
# 			not_cluster_heads.remove(Node.id)
# 			round_wise_cluster_head.append(Node)

# 	if(len(round_wise_cluster_head) == 0):
# 		for Node in net.node_list:
# 			if(len(round_wise_cluster_head) < int(1/P) and rnds  - Node.last_head_rnd >= int(1/P)):
# 				round_wise_cluster_head.append(Node)

# 		if(len(round_wise_cluster_head) == 0):
# 			failed_iterations+= 1
# 			continue

# 	print(len(round_wise_cluster_head), end = " ")
# 	for x in round_wise_cluster_head:
# 		print(x.id, end = " ")
# 	print()

# 	#	create clusters
# 	for Node in net.node_list:
# 		if Node.role == 0:
# 			for head in round_wise_cluster_head:
# 				if Node.dist_to_head > Node.dist(head):
# 					Node.clusterID = head.id
# 					Node.dist_to_head = Node.dist(head)
# 			print(Node.id, " : ", Node.clusterID)
# 			headNode = net.node_map[Node.clusterID]
# 			headNode.children_clusters.append(Node)


# 	#Data Transmission


# 	quant={int:int}
# 	for i in range(net.number_of_nodes + 1):
# 		quant[i] = 0
# 	for Node in net.node_list:
# 		if Node.role == 0:

# 			headNode = net.node_map[Node.clusterID]
# 			trns=Node.energy_for_transmission(net.packet_length, Node.dist_to_head)

# 			recep=headNode.energy_for_reception(net.packet_length)

# 			if(headNode.current_energy > recep):
# 				if(Node.current_energy > trns):
# 					p_gen+=1
# 					Node.current_energy -= trns
# 					energy_consumed+=trns
# 					headNode.current_energy -= recep
# 					energy_consumed+=recep
# 					rnd_latency+=(net.latency(Node,headNode))
# 					quant[Node.clusterID]+=1


# 	for Node in net.node_list:
# 		if Node.role == 1:

# 			while quant[Node.id]:
# 				snk=Node.energy_for_transmission(net.packet_length, Node.dist(sink))
# 				if(snk>Node.current_energy):
# 					break
# 				s_trans += 1
# 				quant[Node.id] -= 1
# 				Node.current_energy -= snk
# 				energy_consumed+=snk
# 				rnd_latency+=(net.latency(Node,sink))
# 			snk=Node.energy_for_transmission(net.packet_length, Node.dist(sink))
# 			if(snk<=Node.current_energy):
# 				p_gen +=1
# 				s_trans+=1
# 				Node.current_energy -= snk
# 				energy_consumed+=snk
# 				rnd_latency+=(net.latency(Node,sink))







# #for better throughput
# 	# for Node in net.node_list: #send data from all heads
# 	# 	if Node.role == 1:
# 	# 		snk=Node.energy_for_transmission(net.packet_length, Node.dist(sink))
# 	# 		if(snk<=Node.current_energy):
# 	# 			p_gen +=1
# 	# 			s_trans+=1
# 	# 			Node.current_energy -= snk
# 	# 			energy_consumed+=snk
# 	# 			rnd_latency+=(net.latency(Node,sink))

# 	# for Node in net.node_list:
# 	# 	if Node.role == 0:
# 	# 		headNode = net.node_map[Node.clusterID]
# 	# 		trns=Node.energy_for_transmission(net.packet_length, Node.dist_to_head)
# 	# 		recep=headNode.energy_for_reception(net.packet_length)

# 	# 		if(headNode.current_energy > recep):
# 	# 			if(Node.current_energy > trns):
# 	# 				p_gen+=1
# 	# 				Node.current_energy -= trns
# 	# 				energy_consumed+=trns
# 	# 				headNode.current_energy -= recep
# 	# 				energy_consumed+=recep #recieved at head
# 	# 				snk=headNode.energy_for_transmission(net.packet_length, headNode.dist(sink))
# 	# 				if(snk<=headNode.current_energy):
# 	# 					s_trans+=1
# 	# 					headNode.current_energy -= snk
# 	# 					energy_consumed+=snk
# 	# 					rnd_latency+=(net.latency(headNode,sink))

# 	print(Node.id, " : ", Node.current_energy)
# 	print(s_trans ,p_gen,s_trans/p_gen)
# 	# operation_log.append([rounds, operational_nodes, net.node_list, [Node.id for Node in dead_nodes]])

# total_latency+=rnd_latency
# # for log in operation_log:
# # 	print("round no. : ", log[0])
# # 	print("operational nodes: ", log[1])
# # 	print(log[2])
# if(failed_iterations >= 200):
# 	print("failed!")
# print("round no. : ", rnds)


# avg_latency= total_latency/rnds

# print("Average latency : ",avg_latency)

# print("Throughput : ",s_trans/p_gen)
# print("Total Energy Consumed : ",energy_consumed)

