import networkx as nx
from node import *
from network import *
import math
from numpy.random import normal

def drop_packs(trasn_packs):
	return max(math.floor(normal(trasn_packs*0.07, 2)),0)

hist = []
def node2NodeTransmission(curr, next):
	et = curr.energy_for_transmission(k, next.dist(curr))
	transferred_packets = min(curr.packets_this_rnd, math.ceil(curr.current_energy/et))
	curr.current_energy -= (transferred_packets*et)
	dropped_p = drop_packs(transferred_packets)
	hist.append([transferred_packets, dropped_p])
	received_packets = max(transferred_packets - dropped_p, 0)
	next.current_energy -= (received_packets*er)
	next.packets_this_rnd += received_packets
	return lm[curr.id][next.id]

def add_dead_node(c):
	if c.current_energy < c.critical_energy:
		dead_nodes.add(c.id)
		try:
			net.nxg.remove_node(c.id)
		except:
			pass
	return c.current_energy < c.critical_energy


net = network(500, 500, 400, 0, 0)
# path = "results/ppo/result/0-graph_data.npy"
srtr = "cl-conv"
path = "results/network_data/network1network_data.npy"
parent_dir = "results/fsw-ppo/"
graph_data = net.load_network(path,1)
net.show_graph()

#initial residual energy:
net.packet_length= 16
packets = 10

for n in net.node_list:
	n.current_energy = 40
	n.critical_energy = 0.0
	n.set_packets(packets)

sink = net.sink
dead_nodes = set()
k = net.packet_length
N = net.number_of_nodes
rnds=0
er = sink.energy_for_reception(k)
net.calculate_latency()
lm=net.latency_matrix
dm=net.calculate_dist()
e_rounds = []
l_rounds = []
th_rounds = []
live_nodes = []
ch_msg = {}
ch = {}
clusters_count = 0
failed_itr_per_node = {}
P = 0.35
failed_iterations = 0
clusters = []

#setting distance from server in every node:
for Node in net.node_list:
	Node.dist(sink)
	Node.setup_for_leach()
	failed_itr_per_node[Node] = 0
	ch_msg[Node] = 0

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

for Node in net.node_list:
	if Node.role == 0:
		Node.dist_to_head = 1e9
		for i in range(clusters_count):
			head = ch[i]
			d = Node.dist(head)
			if Node.dist_to_head != min(Node.dist_to_head, d):
				Node.dist_to_head = d
				Node.clusterID = i
		clusters[Node.clusterID].add(Node)


while len(dead_nodes) < 0.9*N:
	message_gen = (N - len(dead_nodes))*packets
	e=0
	l=0
	sink.packets_this_rnd=0

	for Node in net.node_list:
		head=ch[Node.clusterID]
		Node.set_packets(packets)
		if Node.id in dead_nodes or Node.id == 1:
			continue
		l += node2NodeTransmission(Node,head)
		add_dead_node(Node)
		# if Node.current_energy < Node.critical_energy:
		# 	dead_nodes.add(Node.id)
		# 	net.nxg.remove_node(Node.id)

		e += max(Node.current_energy, Node.critical_energy)

	for Node in net.node_list:
		if Node.role == 1 and Node.id not in dead_nodes:

			l+=node2NodeTransmission(Node, sink)

			if Node.current_energy < Node.critical_energy:
				dead_nodes.add(Node.id)
				net.nxg.remove_node(Node.id)
				cID=Node.clusterID
				for member in clusters[cID]:
					dead_nodes.add(member.id)
					try:
						net.nxg.remove_node(Node.id)
					except:
						pass

			e += max(Node.current_energy, Node.critical_energy)

	l_rounds.append(l)
	e_rounds.append(e)
	th_rounds.append(round(sink.packets_this_rnd/message_gen, 3))
	live_nodes.append(N - len(dead_nodes))
	rnds += 1


print(rnds)
parent_dir='final-meet/'
net.save_network_performance(parent_dir + "/leach-0.35-drop",srtr,rnds,e_rounds,th_rounds,l_rounds,live_nodes)