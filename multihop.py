from network import *
import math
from numpy.random import normal
from networkx.exception import NetworkXNoPath

hist = []
def drop_packs(trasn_packs):
	return max(math.floor(normal(trasn_packs*0.07, 2)),0)

def node2NodeTransmission(curr, next):
	et = curr.energy_for_transmission(k, next.dist(curr))
	transferred_packets = min(curr.packets_this_rnd, math.ceil(curr.current_energy/et))
	curr.current_energy -= (transferred_packets*et)
	dropped_p = drop_packs(transferred_packets)
	hist.append([transferred_packets, dropped_p])
	received_packets = max(transferred_packets - dropped_p, 0)
	next.current_energy -= (received_packets*er)
	next.packets_this_rnd += received_packets
	return received_packets*lm[curr.id][next.id]

def add_dead_node(c):
	if c.current_energy < c.critical_energy:
		dead_nodes.add(c.id)
		try:
			net.nxg.remove_node(Node.id)
		except:
			pass
	return c.current_energy < c.critical_energy

net = network(500, 500, 400, 0, 0)
path = "results/gsw-ppo/result/0-graph_data.npy"
# path = "results/network_data/network1network_data.npy"
parent_dir = "results/fsw-ppo/"
graph_data = net.load_network(path, 0)
net.show_graph()
#initialises node

#initial residual energy:
net.packet_length=128
packets = 50

for n in net.node_list:
	n.current_energy = 40
	n.critical_energy = 0.0
	n.set_packets(packets)


dead_nodes = set()
N = net.number_of_nodes
k = net.packet_length
sink = net.sink
net.calculate_latency()
er = sink.energy_for_reception(k)
lm=net.latency_matrix
dm=net.calculate_dist()
e_r = []
l_r= []
th_r= []
live_nodes = []
rnds=0

while len(dead_nodes) < 0.9*N:
	message_gen = (N - len(dead_nodes))*packets
	e=0
	l=0
	sink.packets_this_rnd=0
	for Node in net.node_list:
		if Node.id in dead_nodes:
			continue
		Node.set_packets(packets)
		try:
			path=nx.shortest_path(net.nxg, Node.id, 0)
			path.reverse()
			while len(path) != 2:
				c = net.node_map[path.pop()]
				n = net.node_map[path[-1]]
				l += node2NodeTransmission(c, n)
				add_dead_node(c)
				if add_dead_node(n):
					break
		except:
			path=[0,Node.id]
		finally:
			curr = net.node_map[path.pop()]
			sink = net.node_map[path[-1]]
			l+= node2NodeTransmission(Node,sink)
			add_dead_node(Node)
		e += max(Node.current_energy, Node.critical_energy)
	l_r.append(l)
	e_r.append(e)
	th_r.append(round(sink.packets_this_rnd/message_gen, 3))
	live_nodes.append(N - len(dead_nodes))
	rnds += 1

print(rnds)
parent_dir='final-meet/'
net.save_network_performance(parent_dir + "/multihop-drop","fl-gsw",rnds,e_r,th_r,l_r,live_nodes)
