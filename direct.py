from network import network

net = network(500, 500, 400, 0, 0)
net.initialise_nodes_fixed(1, 0.4)
net.set_parameters(2000,200,2000,2000, 50)

dead_node = set()
n = net.number_of_nodes
k = net.packet_length
sink = net.sink
packets = 0
rnd = 0
op_log = []
# net.show_network()
total_latency=0
while len(dead_node) < 0.9 * net.number_of_nodes:
	p = []
	rnd_latency=0
	for x in net.node_list:
		d=x.dist(sink)
		et = x.energy_for_transmission(k,d)
		if not x.is_functional() or et > x.current_energy:
			if x not in dead_node:
				dead_node.add(x)
				n-=1
			continue

		rnd_latency+=(net.latency(x,sink))

		x.current_energy -= et
		packets+= 1

	print(n)
	for x in net.node_list:
		if x in dead_node:
			continue
		print(f"{x.id} : {x.current_energy} , {x.energy_for_transmission(k, x.dist(sink))}")
		p.append([x.id, x.current_energy, x.energy_for_transmission(k, x.dist(sink))])
	total_latency+=rnd_latency
	rnd += 1
	op_log.append(p)


print("rounds : ", rnd)
print(packets)
avg_latency= total_latency/rnd

print("Average latency : ",avg_latency)

