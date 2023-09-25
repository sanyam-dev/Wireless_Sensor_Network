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
		net.initialise_nodes_fixed(1, 1e-3)
		net.set_parameters(2000, 8, 2000, 3*1e8, 50)
		#load graph

		graph_data = np.load(graph_data_path, allow_pickle=True).item()
	else:
		_, _, graph_data = net.load_network_topology(graph_data_path)

	return graph_data

graph_data_path = "results/result39/4-graph_data.npy"
# graph_data_path = "results/network_data/network1network_data.npy"
graph_data= load_network(graph_data_path, 0)

#for ppo
G = net.set_nxg_from_npy(graph_data)
# G = net.set_nxg()
net.show_graph()

s_trans = 0		
p_gen = 0
energy_consumed=0
total_latency=0
rnd_latency=0

sink = net.sink
dead_node = set()
k = net.packet_length
rnds = 0
n = net.number_of_nodes
n_map = net.node_map

energy_for_reception = n_map[1].energy_for_reception(k)

for i in range(1, n + 1):
    curr = n_map[i]
    curr.dist(sink)
    curr.setup_for_leach()

P = 0.04
not_cluster_heads = set(i for i in range(1, n + 1))
failed_iterations = 0
operational_nodes=n

while len(dead_node) < 0.9*n:
	print("length of dead nodes ",len(dead_node))
	# print(G.number_of_nodes())
	total_latency+=rnd_latency
	rnd_latency=0
	rnds+=1
	round_wise_cluster_head = []
	rnd_latency=0
	for i in range(1, n + 1):
		if i in dead_node:
			continue

		Node = n_map[i]
		Node.role = 0
		print("current and critical energy of node ",i," ", Node.current_energy, Node.critical_energy)
		if Node.critical_energy > Node.current_energy:
			operational_nodes = operational_nodes - 1
			dead_node.add(i)
			print("critical : ", Node.critical_energy)
			# print("added in dead node", i)
			try:
				G.remove_node(i)
			except:
				continue

			continue
		
		if i in dead_node:
			continue

		# print("vinitial" ,Node.last_head_rnd, rnds, Node.last_head_rnd - rnds)

		if( rnds  - Node.last_head_rnd  > int(1/P)):
			# print("negative or positive" ,Node.last_head_rnd, rnds, Node.last_head_rnd - rnds)
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
			# print("adding in head", i," ",Node.id," ", Node.current_energy, Node.critical_energy)

			

	if(len(round_wise_cluster_head) == 0):
		for i in range(1,n+1):
			Node= n_map[i]
		
			if i in dead_node:
				continue
			elif(len(round_wise_cluster_head) < int(1/P) and rnds  - Node.last_head_rnd >= int(1/P)):
				round_wise_cluster_head.append(Node)
				# print("adding in head", i," ",Node.id, " ", Node.current_energy, Node.critical_energy)
				Node.role=1


		if(len(round_wise_cluster_head) == 0):
			failed_iterations+= 1
			continue

	print("headnode node length",len(round_wise_cluster_head), end = " ")
	for x in round_wise_cluster_head:
		print(x.id, end = " ")
	print()

	for i in range(1,n+1):
		# print("here")
		
		Node= n_map[i]
		if Node.role == 0:
			Node.dist_to_head=1e5
			for head in round_wise_cluster_head:
				if Node.dist_to_head > Node.dist(head):
					Node.clusterID = head.id
					Node.dist_to_head = Node.dist(head)
			# print("getting id",Node.id, " :: ", Node.clusterID)
			headNode = net.node_map[Node.clusterID]
			headNode.children_clusters.append(Node)


#data transmission

	quant={int:int}
	for i in range(1,n+1):
		quant[i] = 0


	for i in range(1, n + 1):
		Node = n_map[i]
		print(Node.id, " : ", Node.current_energy)
		if i in dead_node:
			# print("continues")
			continue

		
		if Node.role == 0:
			headNode = net.node_map[Node.clusterID]
			trns=Node.energy_for_transmission(net.packet_length, Node.dist_to_head)
			recep=headNode.energy_for_reception(net.packet_length)
			print("energy for trns and recep", Node.dist_to_head, trns , recep)
			print("headnode energy :" , Node.clusterID, ":", headNode.current_energy)

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
		Node = n_map[i]
		
		if i in dead_node:
			continue


		if Node.role == 1:

			print("quant :" ,quant[Node.id])
			print("Node.role :" ,Node.role)
			while quant[Node.id]:

				quant[Node.id]-= 1
				curr=Node
				path = net.findShortestPath(curr)
				while len(path) != 0:
					next = net.node_map[path.pop()]
					rnd_latency+=(net.latency(curr,next))
					trns=curr.energy_for_transmission(k, next.dist(curr))
					curr.current_energy -= trns
					recep=next.energy_for_reception(k)
					next.current_energy -= recep
					energy_consumed+=recep
					curr=next

				snk=curr.energy_for_transmission(net.packet_length, curr.dist(net.sink))
				if(curr.id==0):
					
					s_trans+=1
				
				elif curr.current_energy > snk:
					
					curr.current_energy -= snk
					rnd_latency+=(net.latency(curr,sink))
					energy_consumed+=snk
					s_trans += 1

					
	# operation_log.append([rnds, operational_nodes, net.node_list, [n_map[i].id for i in dead_node]])
	if(failed_iterations >= 200):
		print("failed")
		break
	
	print(Node.id, " : ", Node.current_energy)

	print(s_trans ,p_gen,s_trans/p_gen)
	print("energyconsumed :", energy_consumed )
total_latency+=rnd_latency

if(failed_iterations >= 200):
	print("failed!")
print("round no. : ", rnds)


avg_latency= total_latency/rnds

print("Average latency : ",avg_latency)

print("Throughput : ",s_trans/p_gen)
print("Total Energy Consumed : ",energy_consumed)

