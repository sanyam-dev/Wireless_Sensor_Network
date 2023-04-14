from network import *
from node import *

#    	set network
net = network(500, 500, 400, 0, 0)
net.set_parameters(2000,200,2000,2000,30)
net.initialise_nodes(1, 0.2)

# net.show_network()
sink = net.sink
operational_nodes = net.number_of_nodes

#	operational log
dead_nodes = []
rnd = 0
operational_log = []

path = net.dijkstra()
print(path)
packet_length = net.packet_length
dead_nodes = set()
pkt_gen = 0
pkt_rec = 0
while len(dead_nodes) < 0.1 * net.number_of_nodes:
	rnd += 1
	packet_to_sink = 0

	### 	Stable------

	### Latest---
	for i in range(1, net.number_of_nodes + 1):

		if i in dead_nodes:
			continue

		pkt_gen += 1
		curr_id = i
		next_id = path[curr_id][0]
		while next_id != 0:
			currNode = net.node_map[curr_id]
			nextNode = net.node_map[next_id]
			if next_id in dead_nodes:
				next_id = 0
				break

			if currNode.current_energy < currNode.energy_for_transmission(net.packet_length, path[curr_id][1]):
				dead_nodes.add(curr_id)
				operational_nodes -= 1
			elif nextNode.current_energy < nextNode.energy_for_reception(net.packet_length):
				dead_nodes.append(next_id)
				operational_nodes -= 1
			else:
				currNode.current_energy -= currNode.energy_for_transmission(net.packet_length, path[curr_id][1])
				nextNode.current_energy -= nextNode.energy_for_reception(net.packet_length)

			curr_id = 	next_id
			next_id =	path[curr_id][0]
		#	if the next node is sink node:
		currNode = net.node_map[curr_id]
		res = currNode.transmit(packet_length, currNode.dist(sink), sink)
		if(res == -1):
			operational_nodes -= 1
			dead_nodes.add(curr_id)
		else:
			pkt_rec +=1



	print(rnd, pkt_rec, operational_nodes)
	print("----Energy_each_node----")
	for i in net.node_list:
		print(i.current_energy)

print(pkt_rec)
print(pkt_gen)
print(f"number of rounds: {rnd}")

l = []
for i in dead_nodes:
	l.append(net.node_map[i].current_energy)

print(l)
### Stable---

# packets = [1 for i in range(net.number_of_nodes + 1)]
	# packets[0] = 0

	# for i in range(1, net.number_of_nodes + 1):
	# 	Node = net.node_map[i]

	# 	if Node.is_functional() == False:
	# 		operational_nodes -= 1
	# 		continue

	# 	if(path[i] == -1):
	# 		receiver_node = sink
	# 		d = Node.dist(sink)
	# 	else:
	# 		receiver_node = net.node_map[path[i][0]]
	# 		d = path[i][1]

	# 	# print("transsmission info", i, receiver_node.id, d)
	# 	while packets[i] != 0:
	# 		if Node.critical_energy > Node.current_energy: #Node not functional
	# 			operational_nodes -= 1
	# 			break

	# 		elif receiver_node.critical_energy > receiver_node.current_energy: #Receiver not functional
	# 			res = Node.transmit(net.packet_length, Node.dist(sink), sink)
	# 			if res == 0:
	# 				break
	# 			else:
	# 				packets[i] -= 1
	# 				packets[0] += 1

	# 		else:	#Both are functional
	# 			res = Node.transmit(net.packet_length, Node.dist(receiver_node), receiver_node)
	# 			if res == 0:
	# 				break

	# 			packets[i] -=1
	# 			packets[receiver_node.id] += 1

	# 	if Node.is_functional() == False:
	# 		operational_nodes -=1