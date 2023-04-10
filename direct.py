from node import *
from network import *

net = network(500, 500, 400, 0, 0)
net.initialise_nodes(1, 0.2)
net.set_parameters(2000,2000,2000,2000, 20)

dead_node = set()
n = net.number_of_nodes
k = net.packet_length
sink = net.sink
packets = 0
rnd = 0
op_log = []

while len(dead_node) < 0.2*net.number_of_nodes:
	p = []
	for x in net.node_list:
		et = x.energy_for_transmission(k, x.dist(sink))
		if not x.is_functional() or et > x.current_energy:
			if x not in dead_node:
				dead_node.add(x)
				n-=1
			continue

		x.current_energy -= et
		packets+= 1

	print(n)
	for x in net.node_list:
		if x in dead_node:
			continue
		print(f"{x.id} : {x.current_energy} , {x.energy_for_transmission(k, x.dist(sink))}")
		p.append([x.id, x.current_energy, x.energy_for_transmission(k, x.dist(sink))])

	rnd += 1
	op_log.append(p)

	# for i in range(1, net.number_of_nodes+ 1):
	# 	if i in dead_node:
	# 		continue

	# 	Node = net.node_map[i]
	# 	et = Node.energy_for_transmission(k, Node.dist(sink))
	# 	print(et)
	# 	if Node.is_functional() and Node.current_energy > et:
	# 		Node.current_energy -= et
	# 		packets += 1
	# 	else:
	# 		dead_node.add(i)
	# 		n -= 1

	# 	p.append([i,Node.current_energy])
	# print(rnd)
	# if rnd % 5 == 0:
	# 	for Node in net.node_list:
	# 		if Node.is_functional():
	# 			print(f"{Node.id} : {Node.current_energy}")

print("rounds : ", rnd)
print(packets)

