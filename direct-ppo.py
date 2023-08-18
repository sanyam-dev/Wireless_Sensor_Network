import networkx as nx
import numpy as np
from network import *
from node import *

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


graph_data_path = "results/result50/1-graph_data.npy"
# graph_data_path = "results/network_data/network1network_data.npy"
graph_data = load_network(graph_data_path, save_mode=0)
G = net.set_nxg_from_npy(graph_data)
net.show_graph()
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

while G.number_of_nodes() > 0.1*n:

	for i in range(1, n+1):
		if i in dead_node or n_map[i].current_energy < n_map[i].critical_energy:
			try:
				G.remove_node(i)
				dead_node.add(i)
			except:
				continue
			continue

		e = n_map[i].energy_for_transmission(k, n_map[i].dist(sink))
		p_gen += 1
		if(n_map[i].current_energy < e):
			dead_node.add(i)
			G.remove_node(i)
		else:
			n_map[i].current_energy -= e
			energy_consumed += e + energy_for_reception
			rnd_latency += net.latency(n_map[i], sink)
			s_trans += 1
		print(i, round(n_map[i].current_energy, 3), round(e,3))

	rnds +=1
	total_latency += rnd_latency
	rnd_latency = 0
	print("----")
	print(rnds, len(dead_node))
	# s = ""
	for i in range(1, n+1):
		if i not in dead_node:
			# s += i + ": " + round(n_map[i].current_energy, 3)
			print(i, ": ", round(n_map[i].current_energy, 3))
	print("----")


total_latency+=rnd_latency

avg_latency= total_latency/rnds
print(rnds)

print("Average latency : ",round(avg_latency, 3))
print("Throughput : ",round(s_trans/p_gen, 3))
print("Total Energy Consumed : ",round(energy_consumed, 3))