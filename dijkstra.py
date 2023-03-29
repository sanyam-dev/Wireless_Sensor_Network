from network import *
from node import *

#	set network
net = network(100, 100, 40, 0, 0)
net.set_parameters(2000,2000,2000,2000, 30)
net.initialise_nodes(1, 0.2)
net.show_network()
sink = [net.base_station_x, net.base_station_y]
operational_nodes = net.number_of_nodes

#	operational log
dead_nodes = []
rnds = 0
operational_log = []

net.network_adj_matrix()

# 	n_list = adj[Node.id]
# 	for Node in net.node_list:
# 	print(Node.id, end  = ": ")
# 	for x in n_list:
# 		print(f"({x[0].id}), ({x[1]})", end = ", ")
# 	print()


shortest_paths = net.dijkstra()

prev_round_operational_nodes = operational_nodes

while operational_nodes > 0:
	rnds += 1

	if(prev_round_operational_nodes != operational_nodes):
		prev_round_operational_nodes = operational_nodes
		shortest_paths = net.dijkstra()

	for Node in net.node_list:
		path = shortest_paths[Node]
		Node.current_energy -= Node.energy_for_transmission(net.packet_length,
						      Node.dist_from_node(path[0]))

		currNode = path.pop(0)
		while(len(path) != 0):
			currNode.current_energy -= currNode.energy_for_reception(net.packet_length)
			currNode.current_energy -= currNode.energy_for_transmission(net.packet_length,
							       currNode.dist_from_node(path[0]))

			if(currNode.critical_energy > currNode.current_energy):
				operational_nodes -= 1





#	Average Path Length
# APL = 0
# for i in dp:
# 	APL += i

# APL /= net.number_of_nodes
# APL = round(APL, 2)
# print(APL)
# dp = sorted(dp, reverse = True)
# print(dp)

