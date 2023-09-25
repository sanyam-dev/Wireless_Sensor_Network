import networkx as nx
import pickle
import numpy as np
from node import *
from network import *

#weight function
def weight(u, v, G):
	try:
		return G[u][v]['weight'] if G[u][v]['weight'] > n_map[u].current_energy else 1e9
	except:
		return 1e9

def check_path(path):
	n = len(path)
	path_sum =0
	for i in range(n - 1):
		curr = path[i]
		next = path[i+1]
		path_sum += G[curr][next]['weight']
		if(G[curr][next]['color'] == 'red'):
			print("red!")
	print("pathsum : ",  path_sum)
	return path_sum < 1e9

def dist(a, b):
	(x1, y1) = a
	(x2, y2) = b
	return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

#load ppo graph data
# graph_data_path = "results/result32/0-graph_data.npy"
graph_data_path = "results/result11/0-graph_data.npy"
graph_data = np.load(graph_data_path, allow_pickle=True).item()

#initialise network
net = network(500, 500, 400, 0, 0)
net.initialise_nodes_fixed(1, 0)
net.set_parameters(2000, 8, 2000, 3*1e8, 50)

sink = net.sink
dead_node = set()
k = net.packet_length
rnds = 0
n = net.number_of_nodes
n_map = net.node_map

total_latency=0
energy_consumed=0
s_trans = 0		#	successful transactions
p_gen = 0	#	messages generated
rnd_latency=0
energy_for_reception = n_map[1].energy_for_reception(k)


G = net.set_nxg_from_npy(graph_data)
# G = net.set_nxg()
net.show_graph()


# try:
# 	path = list(nx.astar_path(G, 4, 0,weight= weight))
# except:
# 	path = list(nx.shortest_path(G, 1, 0, weight=weight))


# print(path)

# if check_path(path):
# 	for i_id in range(len(path) - 1):
# 		curr_node_id = path[i_id]
# 		next_node_id = path[i_id + 1]
# 		curr_node = n_map[curr_node_id]
# 		next_node = n_map[next_node_id]
# 		rnd_latency += net.latency(curr_node, next_node)
# 		curr_node.current_energy -= G[curr_node_id][next_node_id]['weight']
# 		next_node.current_energy -= energy_for_reception
# 		energy_consumed += G[curr_node_id][next_node_id]['weight'] + energy_for_reception


while G.number_of_nodes() > 0.1*n:

	for i in range(1,n+1):
		curr = n_map[i]
		if curr.current_energy < curr.critical_energy or i in dead_node:
			dead_node.add(i)
			try:
				G.remove_node(i)
			except:
				continue
			continue

		#active node message generation
		p_gen += 1
		message_rec_flag = 0

		#define transmission path
		try:
			path = list(nx.astar_path(G, i, 0, weight))
		except:
			try:
				path = list(nx.shortest_path(G, i, 0, weight))
			except:
				# if no paths found, try direct transmission.
				if curr.energy_for_transmission(k, curr.dist(sink)) < curr.current_energy:
					print("message failed! ", i)
					G.remove_node(i)
					dead_node.add(i)
				else:
					curr.current_energy -= curr.energy_for_transmission(k, curr.dist(sink))
					s_trans += 1
				continue

		if check_path(path):
			for i_id in range(len(path) - 1):
				curr_node_id = path[i_id]
				next_node_id = path[i_id + 1]
				curr_node = n_map[curr_node_id]
				next_node = n_map[next_node_id]
				rnd_latency += net.latency(curr_node, next_node)
				curr_node.current_energy -= G[curr_node_id][next_node_id]['weight']
				next_node.current_energy -= energy_for_reception
				energy_consumed += G[curr_node_id][next_node_id]['weight'] + energy_for_reception

			#the message is received by sink
			s_trans += 1
			message_rec_flag = 1
			break

		#if message was not received
		if message_rec_flag == 0:
			dead_node.add(i)
			G.remove_node(i)

	total_latency+=rnd_latency
	rnd_latency=0
	rnds += 1
	print("----")
	print(rnds, len(dead_node))
	print("----")


total_latency+=rnd_latency

avg_latency= total_latency/rnds
print("Rounds : " ,rnds)
print("Average latency : ",avg_latency)
print("Throughput : ",s_trans/p_gen)
print("Total Energy Consumed : ",energy_consumed)