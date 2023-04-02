from node import *
from network import *

#	initialising networkz
net = network(100, 100, 40, 0, 0)

#	setting network parameters: distribution parameters, packet length,
# 	transmission_rate and speed_of_transmission
net.set_parameters(2000, 2000, 2000, 2000, 30)

#	setting node initial_eneregy and node critical_energy to function
net.initialise_nodes(1, 0.2)
# net.show_network()
#copying reocurring network parameters
sink = net.sink
operational_nodes =	net.number_of_nodes
dead_nodes = []
rounds = 0

operation_log = []

#	main loop
while operational_nodes > 0:
	# each node trzansmit data once every round

	for Node in net.node_list:
		if not Node.is_functional():
			operational_nodes = operational_nodes - 1
			dead_nodes.append(Node)
			pass

		res = Node.transmit(net.packet_length, Node.dist(sink), sink)
		# Node.current_energy -= Node.energy_for_transmission(net.packet_length, Node.dts)
		# Node.current_energy -= Node.energy_for_reception(net.packet_length)

		print(Node.id, " : ", Node.current_energy)
	rounds += 1

	operation_log.append([rounds, operational_nodes, [Node.id for Node in dead_nodes]])

	print("round no.: ",rounds)
	print("operational nodes: ", operational_nodes)

