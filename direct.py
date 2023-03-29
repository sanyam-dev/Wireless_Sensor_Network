from node import *
from network import *

#	initialising network
net = network(100, 100, 100, 0, 0)

#	setting network parameters: distribution parameters, packet length,
# 	transmission_rate and speed_of_transmission
net.set_parameters(2000, 2000, 2000, 2000, 30)

#	setting node initial_eneregy and node critical_energy to function
net.initialise_nodes(1, 0.2)
net.show_network()
#copying reocurring network parameters
sink = [net.base_station_x, net.base_station_y]
operational_nodes =	net.number_of_nodes
dead_nodes = []
rounds = 0

operation_log = []

#	setting distance from server in every node:
for Node in net.node_list:
	Node.dist_from_server(sink)

#	main loop
while operational_nodes > 0:
	# each node transmit data once every round

	for Node in net.node_list:
		if Node.critical_energy > Node.current_energy:
			operational_nodes = operational_nodes - 1
			dead_nodes.append(Node)
			pass

		Node.current_energy -= Node.energy_for_transmission(net.packet_length, Node.dts)
		Node.current_energy -= Node.energy_for_reception(net.packet_length)

		print(Node.id, " : ", Node.current_energy)
	rounds += 1

	operation_log.append([rounds, operational_nodes, [Node.id for Node in dead_nodes]])

	print("round no.: ",rounds)
	print("operational nodes: ", operational_nodes)