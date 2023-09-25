import networkx as nx
import numpy as np
from node import *
from network import *
import random

net = network(500, 500, 400, 0, 0)

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
	else:
		_, _, graph_data = net.load_network_topology(graph_data_path)

	return graph_data


graph_data_path = "results/network_data/network1network_data.npy"
graph_data= load_network(graph_data_path, 1)



sink = net.sink
dead_nodes = set()
k = net.packet_length
rnds = 0
n = net.number_of_nodes
n_map = net.node_map


#for ppo
G = net.set_nxg_from_npy(graph_data)
# G = net.set_nxg()
net.show_graph()


s_trans = 0		#	successful transactions
p_gen = 0	#	messages generated
energy_consumed=0
total_latency=0
rnd_latency=0
energy_for_reception = n_map[1].energy_for_reception(k)

# net.show_network()


# operation_log = []

#	setting distance from server in every node:
# for Node in net.node_list:
	# Node.dist(sink)
	# Node.setup_for_leach()
for i in range(1, n + 1):
    curr = n_map[i]
    curr.dist(sink)
    curr.setup_for_leach()

#	LEACH specific parameters
P = 0.04
not_cluster_heads = set(i for i in range(1, n + 1))
failed_iterations = 0
operational_nodes=n

while len(dead_nodes) < 0.9*n:
    # print()
	print(len(dead_nodes))
	#	each node transmit data once every round
	total_latency+=rnd_latency
	rnds += 1
	round_wise_cluster_head = []
	rnd_latency=0
    
    # for i in range(1, n+1):

	#	Advertising Phase
	for i in range(1, n + 1):
		# if i in dead_nodes:
		# 	try:
		# 		G.remove_node(i)
		# 	except:
		# 		continue
		# 	continue
		Node = n_map[i]
		Node.role = 0

		if Node.critical_energy > Node.current_energy:
			operational_nodes = operational_nodes - 1
			dead_nodes.add(Node)
		
			# try:
			# 	G.remove_node(i)
			# except:
			# 	pass
			# pass

		if(Node.last_head_rnd - rnds > int(1/P)):
			not_cluster_heads.add(Node.id)

		Tn = 0

		if Node.id in not_cluster_heads:
			Tn = P/(1 - P*(rnds % int(1/P)))

		response = round(random.uniform(0,1), 3)
		if response < Tn:
			Node.role = 1
			Node.times_elected += 1
			Node.last_head_rnd = rnds
			not_cluster_heads.remove(Node.id)
			round_wise_cluster_head.append(Node)


	if(len(round_wise_cluster_head) == 0):
		for i in range(1,n+1):
			Node= n_map[i]

			if(len(round_wise_cluster_head) < int(1/P) and rnds  - Node.last_head_rnd >= int(1/P)):
				round_wise_cluster_head.append(Node)

		if(len(round_wise_cluster_head) == 0):
			failed_iterations+= 1
			continue

		
	# print(len(round_wise_cluster_head), end = " ")
	# for x in round_wise_cluster_head:
		# print(x.id, end = " ")
	# print()

	#	create clusters
	for i in range(1,n+1):
		# if i in dead_nodes:
		# 	try:
		# 		G.remove_node(i)
		# 	except:
		# 		continue
		# 	continue

		Node = n_map[i]

		if Node.role == 0:
			for head in round_wise_cluster_head:
				if Node.dist_to_head > Node.dist(head):
					Node.clusterID = head.id
					Node.dist_to_head = Node.dist(head)
			# print(Node.id, " : ", Node.clusterID)
			headNode = net.node_map[Node.clusterID]
			headNode.children_clusters.append(Node)


	# #Data Transmission


	quant={int:int}
	for i in range(1,n+1):
		quant[i] = 0


	
	for i in range(1, n + 1):
		# if i in dead_nodes:
		# 	try:
		# 		G.remove_node(i)
		# 	except:
		# 		continue
		# 	continue

		Node = n_map[i]
		if Node.role == 0:

			headNode = net.node_map[Node.clusterID]
			trns=Node.energy_for_transmission(net.packet_length, Node.dist_to_head)

			recep=headNode.energy_for_reception(net.packet_length)

			if(headNode.current_energy > recep):
				if(Node.current_energy > trns):
					p_gen+=1
					Node.current_energy -= trns
					energy_consumed+=trns
					headNode.current_energy -= recep
					energy_consumed+=recep
					rnd_latency+=(net.latency(Node,headNode))
					quant[Node.clusterID]+=1



	for i in range(1, n + 1):
		# if i in dead_nodes:
		# 	try:
		# 		G.remove_node(i)
		# 	except:
		# 		continue
		# 	continue

		Node = n_map[i]

		if Node.role == 1:

			while quant[Node.id]:
				snk=Node.energy_for_transmission(net.packet_length, Node.dist(sink))
				if(snk>Node.current_energy):
					break
				s_trans += 1
				quant[Node.id] -= 1
				Node.current_energy -= snk
				energy_consumed+=snk
				rnd_latency+=(net.latency(Node,sink))
			snk=Node.energy_for_transmission(net.packet_length, Node.dist(sink))
			if(snk<=Node.current_energy):
				p_gen +=1
				s_trans+=1
				Node.current_energy -= snk
				energy_consumed+=snk
				rnd_latency+=(net.latency(Node,sink))


	# print(Node.id, " : ", Node.current_energy)
	# print(s_trans ,p_gen,s_trans/p_gen)


total_latency+=rnd_latency

if(failed_iterations >= 200):
	print("failed!")

print(list_0, len(list_0))
avg_latency= total_latency/rnds
print(rnds)
print("Average latency : ",avg_latency)
print("Throughput : ",s_trans/p_gen)
print("Total Energy Consumed : ",energy_consumed)

