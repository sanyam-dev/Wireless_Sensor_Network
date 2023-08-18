import networkx as nx
import numpy as np
from node import *
from network import *


net = network(500, 500, 400, 0, 0)

def load_network(graph_data_path, save_mode):
	"""
	save_mode: 0 -> old network data
	save_mode: 1 -> new network data
	"""
	if(save_mode == 0):
		net.initialise_nodes_fixed(1, 0.4)
		net.set_parameters(2000, 200, 2000, 3*1e8, 50)
		#load graph

		graph_data = np.load(graph_data_path, allow_pickle=True).item()
	else:
		_, _, graph_data = net.load_network_topology(graph_data_path)

	return graph_data



#initialise network
# graph_data_path = "results/result32/0-graph_data.npy"
graph_data_path = "results/result7/0-graph_data.npy"
# graph_data_path = "results/network_data/network1network_data.npy"
graph_data= load_network(graph_data_path, 0)



sink = net.sink
dead_node = set()
k = net.packet_length
rnds = 0
n = net.number_of_nodes
n_map = net.node_map



#for ppo
G = net.set_nxg_from_npy(graph_data)
# G = net.set_nxg()
net.show_graph()

#weight function
def weight(u, v, G):
	try:
		return G[u][v]['weight'] if G[u][v]['weight'] > n_map[u].current_energy else 1e9
	except:
		return 1e9


def check_path(path):
	return True
	# n = len(path)
	# path_sum =0
	# for i in range(n - 1):
	# 	curr = path[i]
	# 	next = path[i+1]
	# 	path_sum += G[curr][next]['weight']
	# return path_sum < 1e9

total_latency=0
energy_consumed=0
s_trans = 0		#	successful transactions
p_gen = 0	#	messages generated
rnd_latency=0
energy_for_reception = n_map[1].energy_for_reception(k)


list_0 = [n for n in G[0]]


while G.number_of_nodes() > 0.1*n:

	total_latency+=rnd_latency
	rnd_latency=0

	for i in range(1, n + 1):
		if i in dead_node:
			try:
				G.remove_node(i)
			except:
				continue
			continue

		curr = n_map[i]
		if curr.current_energy < curr.critical_energy:
			dead_node.add(i)
			G.remove_node(i)
			continue

		#active node message generation
		p_gen += 1
		path = net.findShortestPath(curr)

		# print(i, path)
		while len(path) != 0:

			next = net.node_map[path.pop()]
			rnd_latency+=(net.latency(curr,next))
			trns=curr.energy_for_transmission(k, next.dist(curr))
			curr.current_energy -= trns
			recep=next.energy_for_reception(k)
			next.current_energy -= recep
			energy_consumed+=recep
			curr = next

		snk=curr.energy_for_transmission(k, curr.dist(net.sink))
		if curr.id == 0:
			s_trans += 1
		elif curr.current_energy > snk:
			curr.current_energy -= snk
			rnd_latency+=(net.latency(curr,sink))
			energy_consumed+=snk
			s_trans += 1
		elif curr.id == i:
			dead_node.add(i)
			G.remove_node(i)
		# message_rec_flag = 0
		# try:
		# 	path = nx.dijkstra_path(G, i, 0, weight)
		# except:
		# 	#if no paths found, try direct transmission.
		# 	if curr.energy_for_transmission(k, curr.dist(sink)) < curr.current_energy:
		# 		print("message failed!")
		# 		G.remove_node(i)
		# 		dead_node.add(i)
		# 	else:
		# 		curr.current_energy -= curr.energy_for_transmission(k, curr.dist(sink))
		# 		s_trans += 1
		# 	continue

		# # for path in paths_list:
		# 	# if check_path(path):
		# for i_id in range(len(path) - 1):
		# 	curr_node_id = path[i_id]
		# 	next_node_id = path[i_id + 1]
		# 	curr_node = n_map[curr_node_id]
		# 	next_node = n_map[next_node_id]
		# 	rnd_latency += net.latency(curr_node, next_node)
		# 	curr_node.current_energy -= G[curr_node_id][next_node_id]['weight']
		# 	next_node.current_energy -= energy_for_reception
		# 	energy_consumed += G[curr_node_id][next_node_id]['weight'] + energy_for_reception
		# print("path complete! :" , i)
		# #the message is received by sink
		# s_trans += 1
		# message_rec_flag = 1

		# #if message was not received
		# if message_rec_flag == 0:
		# 	dead_node.add(i)
		# 	G.remove_node(i)


	rnds += 1
	print("----")
	print(rnds, len(dead_node))
	for i in range(1, n+1):
		if i not in dead_node:
			print(i, ": ", round(n_map[i].current_energy, 3))
	print("----")


print(list_0, len(list_0))

total_latency+=rnd_latency

avg_latency= total_latency/rnds
print(rnds)
print("Average latency : ",round(avg_latency, 3))
print("Throughput : ",round(s_trans/p_gen, 3))
print("Total Energy Consumed : ",round(energy_consumed, 3))