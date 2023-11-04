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
		net.initialise_nodes_fixed(1, 0)
		net.set_parameters(2000, 8, 2000, 3*1e8, 50)
		#load graph

		graph_data = np.load(graph_data_path, allow_pickle=True).item()
	else:
		_, _, graph_data = net.load_network_topology(graph_data_path)

	return graph_data



#initialise network
graph_data_path = "results/result39/0-graph_data.npy"
# graph_data_path = "results/result88/7-graph_data.npy"
# graph_data_path = "results/network_data/network1network_data.npy"
graph_data= load_network(graph_data_path, 0)

for Node in net.node_list:
	Node.critical_energy = 0


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
net.calculate_latency()
lm = net.latency_matrix
prev_round_energy_consumed = 0
energy_per_round = []
latency_per_round = []
throughput_per_round = []

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
		# try:
		# 	path = nx.shortest_path(G, i, 0, weight, "dijkstra")
		# except:
		path = net.findShortestPath(curr)

		print(i, path)
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


	rnds += 1
	print("----")
	print(rnds, len(dead_node))
	for i in range(1, n+1):
		if i not in dead_node:
			print(i, ": ", round(n_map[i].current_energy, 3))
	latency_per_round.append(rnd_latency)
	energy_per_round.append(energy_consumed - prev_round_energy_consumed)
	prev_round_energy_consumed = energy_consumed
	throughput_per_round.append([p_gen, s_trans, round(s_trans/p_gen, 3)])
	s_trans = 0
	p_gen = 0
	print("----")


print(list_0, len(list_0))
lat = 0
for i in latency_per_round:
	lat += i
avg_latency = lat/len(latency_per_round)
x = 0
avg_throughput = ((x + i[2]) for i in throughput_per_round)/len(throughput_per_round)
print(rnds, len(throughput_per_round))

print("Average latency : ",round(avg_latency, 3))
print("Throughput : ",round(avg_throughput, 3))
print("Total Energy Consumed : ",round(energy_consumed, 3))










def run():

	active_nodes = G.number_of_nodes
	message_generated = active_nodes
	e_tot = 0
	l_tot = 0
	s_trans = 0
	for Node in net.node_list:
		id = Node.id
		all_paths = list(nx.all_simple_paths(G, id, 0))
		#access each path
		best_path = access_paths(all_paths)
		if best_path == []:
			best_path = net.findShortestPath(Node)
			best_path.insert(0, id)
			best_path.append(0)
			#do better

		e_path,l_path,msg = follow_path(best_path)
		e_tot += e_path
		l_tot += l_path
		s_trans += msg

	energy_per_round.append(e_tot)
	latency_per_round.append(l_tot)
	throughput_per_round.append([s_trans, message_generated])


	# do after each round
	for Node in net.node_list:
		if Node.critical_energy > Node.current_energy:
			G.remove_node(Node.id)
			dead_node.append(Node)





def access_paths(all_simple_paths) -> list:
	if len(all_simple_paths) == 0:
		return []

	min_e_path = 1e9
	best_path = []
	e_path = 0
	for path in all_simple_paths:
		path = list(path)
		e_path = calculate_e_path(path)
		if e_path < min_e_path:
			min_e_path = e_path
			best_path = path
	return best_path


def calculate_e_path(path:list):
	e_path = 0
	curr = net.node_map[path[0]]

	for i in range(1, len(path)):
		next = net.node_map[path[i]]
		if(curr.current_energy < curr.energy_for_transmission(k, next.dist(curr)) or next.current_energy < next.energy_for_reception(k)):
			return 1e9
		e_path += curr.energy_for_transmission(k, next.dist(curr)) + next.energy_for_reception(k)
		curr = next

	return e_path/len(e_path)

def follow_path(path):
	e_path = 0
	l_path = 0
	curr = net.node_map[path[0]]

	for i in range(1, len(path)):
		next = net.node_map[path[i]]
		e_path += curr.energy_for_transmission(k, next.dist(curr)) + next.energy_for_reception(k)
		curr.current_energy -= curr.energy_for_transmission(k, next.dist(curr))
		next.current_energy -= next.energy_for_reception(k)
		l_path += lm[curr.id][next.id]
		curr = next

	if curr==sink:
		msg = 1
	else:
		0
	return e_path, l_path, msg

