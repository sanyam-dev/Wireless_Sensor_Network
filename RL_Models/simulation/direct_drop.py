from network import *
from node import *
import network as nx
import math

def drop_packs(trasn_packs):
	return max(math.floor(normal(trasn_packs*0.07, 2)),0)

def node2NodeTransmission(curr, next):
	et = curr.energy_for_transmission(k, next.dist(curr))
	transferred_packets = min(curr.packets_this_rnd, math.ceil(curr.current_energy/et))
	curr.current_energy -= (transferred_packets*et)
	dropped_p = drop_packs(transferred_packets)
	received_packets = max(transferred_packets - dropped_p, 0)
	next.current_energy -= (received_packets*er)
	next.packets_this_rnd += received_packets
	return lm[curr.id][next.id]

net = network(500, 500, 400, 0, 0)
path = "results/network_data/network1network_data.npy"
srtr = "fl-conv"
# path = "results/nsw-ppo/result/0-graph_data.npy"
gd=net.load_network(path,1)


net.packet_length=8
packets=10

for n in net.node_list:
	n.curent_energy= 40
	n.critical_energy = 0.0
	n.set_packets(packets)

dead_nodes=set()
N = net.number_of_nodes
k = net.packet_length
sink = net.sink
rnd = 0
net.calculate_latency()
lm = net.latency_matrix
e_r = []
l_r = []
th_r = []
avg_lat_r = []
live_nodes = []
rnds=0

total_latency=0
rnd_latency=0
er = sink.energy_for_reception(k)

while len(dead_nodes) < 0.9*N:
	message_gen = (N - len(dead_nodes))*packets
	e=0
	l=0
	sink.packets_this_rnd=0
	for Node in net.node_list:
		if Node.id in dead_nodes:
			continue
		Node.set_packets(packets)
		# try:
		# 	path=nx.shortest_path(net.nxg, Node.id, 0)
		# except:
		# 	pass
		# finally:
		l+= node2NodeTransmission(Node,sink)
		if Node.current_energy < Node.critical_energy:
			dead_nodes.add(Node.id)
			net.nxg.remove_node(Node.id)
		e += max(Node.current_energy, Node.critical_energy)
	l_r.append(l)
	e_r.append(e)
	th_r.append(round(sink.packets_this_rnd/message_gen, 3))
	live_nodes.append(N - len(dead_nodes))
	rnds += 1

print(rnds)
parent_dir='final-meet/'
net.save_network_performance(parent_dir + "/direct-drop",srtr,rnds,e_r,th_r,l_r,live_nodes)