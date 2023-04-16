from network import network

net = network(500, 500, 400, 0, 0)
net.initialise_nodes(1, 0.2)
net.set_parameters(2000,200,2000,2000, 30)

dead_node = set()
n = net.number_of_nodes
k = net.packet_length
sink = net.sink
packets = 0
rnd = 0
op_log = []

while len(dead_node) < 0.9 * net.number_of_nodes:
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


print("rounds : ", rnd)
print(packets)

