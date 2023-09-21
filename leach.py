from network import network
import random
#	initialising network:
net = network(500, 500, 400, 0, 0)



s_trans = 0		#	successful transactions
p_gen = 0	#	messages generated
energy_consumed=0
#	setting network parameters: distribution parameters, packet length,
# 	transmission_rate and speed_of_transmission
net.initialise_nodes_fixed(1, 0.4)
net.set_parameters(2000, 200, 2000, 3*1e8, 50)

#	setting node initial_eneregy and node critical_energy to function
net.show_network()

#	copying reocurring network parameters
sink = net.sink
operational_nodes =	net.number_of_nodes
dead_nodes = []
rounds = 0
total_latency=0
operation_log = []

#	setting distance from server in every node:
for Node in net.node_list:
	Node.dist(sink)
	Node.setup_for_leach()

#	LEACH specific parameters
P = 0.04
not_cluster_heads = set(i for i in range(1, operational_nodes + 1))
failed_iterations = 0

#	main loop
rnd_latency=0
while len(dead_nodes) < 0.9*net.number_of_nodes:
	#	each node transmit data once every round
	total_latency+=rnd_latency
	rounds += 1
	round_wise_cluster_head = []
	rnd_latency=0
	#	Advertising Phase
	for Node in net.node_list:

		Node.role = 0

		if Node.critical_energy > Node.current_energy:
			operational_nodes = operational_nodes - 1
			dead_nodes.append(Node)
			net.node_list.remove(Node)
			pass

		if(rounds - Node.last_head_rnd > int(1/P)):
			not_cluster_heads.add(Node.id)

		Tn = 0

		if Node.id in not_cluster_heads:
			Tn = P/(1 - P*(rounds % int(1/P)))

		response = round(random.uniform(0,1), 3)
		if response < Tn:
			Node.role = 1
			Node.times_elected += 1
			Node.last_head_rnd = rounds
			not_cluster_heads.remove(Node.id)
			round_wise_cluster_head.append(Node)

	if(len(round_wise_cluster_head) == 0):
		for Node in net.node_list:
			if(len(round_wise_cluster_head) < int(1/P) and rounds  - Node.last_head_rnd >= int(1/P)):
				round_wise_cluster_head.append(Node)

		if(len(round_wise_cluster_head) == 0):
			failed_iterations+= 1
			continue

	print(len(round_wise_cluster_head), end = " ")
	for x in round_wise_cluster_head:
		print(x.id, end = " ")
	print()

	#	create clusters
	for Node in net.node_list:
		if Node.role == 0:
			for head in round_wise_cluster_head:
				if Node.dist_to_head > Node.dist(head):
					Node.clusterID = head.id
					Node.dist_to_head = Node.dist(head)
			print(Node.id, " : ", Node.clusterID)
			headNode = net.node_map[Node.clusterID]
			headNode.children_clusters.append(Node)


	#Data Transmission


	quant={int:int}
	for i in range(net.number_of_nodes + 1):
		quant[i] = 0
	for Node in net.node_list:
		if Node.role == 0:

			headNode = net.node_map[Node.clusterID]
			trns=Node.energy_for_transmission(net.packet_length, Node.dist_to_head)

			recep=headNode.energy_for_reception(net.packet_length)

			if(headNode.current_energy > recep):
				if(Node.current_energy > trns):
					p_gen+=1
					Node.current_energy -= trns
					energy_consumed+=trns
					headNode.current_energy -= recep
					energy_consumed+=recep
					rnd_latency+=(net.latency(Node,headNode))
					quant[Node.clusterID]+=1


	for Node in net.node_list:
		if Node.role == 1:

			while quant[Node.id]:
				snk=Node.energy_for_transmission(net.packet_length, Node.dist(sink))
				if(snk>Node.current_energy):
					break
				s_trans += 1
				quant[Node.id] -= 1
				Node.current_energy -= snk
				energy_consumed+=snk
				rnd_latency+=(net.latency(Node,sink))
			snk=Node.energy_for_transmission(net.packet_length, Node.dist(sink))
			if(snk<=Node.current_energy):
				p_gen +=1
				s_trans+=1
				Node.current_energy -= snk
				energy_consumed+=snk
				rnd_latency+=(net.latency(Node,sink))

#for better throughput
	# for Node in net.node_list: #send data from all heads
	# 	if Node.role == 1:
	# 		snk=Node.energy_for_transmission(net.packet_length, Node.dist(sink))
	# 		if(snk<=Node.current_energy):
	# 			p_gen +=1
	# 			s_trans+=1
	# 			Node.current_energy -= snk
	# 			energy_consumed+=snk
	# 			rnd_latency+=(net.latency(Node,sink))

	# for Node in net.node_list:
	# 	if Node.role == 0:
	# 		headNode = net.node_map[Node.clusterID]
	# 		trns=Node.energy_for_transmission(net.packet_length, Node.dist_to_head)
	# 		recep=headNode.energy_for_reception(net.packet_length)

	# 		if(headNode.current_energy > recep):
	# 			if(Node.current_energy > trns):
	# 				p_gen+=1
	# 				Node.current_energy -= trns
	# 				energy_consumed+=trns
	# 				headNode.current_energy -= recep
	# 				energy_consumed+=recep #recieved at head
	# 				snk=headNode.energy_for_transmission(net.packet_length, headNode.dist(sink))
	# 				if(snk<=headNode.current_energy):
	# 					s_trans+=1
	# 					headNode.current_energy -= snk
	# 					energy_consumed+=snk
	# 					rnd_latency+=(net.latency(headNode,sink))

	print(Node.id, " : ", Node.current_energy)
	print(s_trans ,p_gen,s_trans/p_gen)
	operation_log.append([rounds, operational_nodes, net.node_list, [Node.id for Node in dead_nodes]])

total_latency+=rnd_latency
# for log in operation_log:
# 	print("round no. : ", log[0])
# 	print("operational nodes: ", log[1])
# 	print(log[2])
if(failed_iterations >= 200):
	print("failed!")
print("round no. : ", rounds)


avg_latency= total_latency/rounds

print("Average latency : ",avg_latency)

print("Throughput : ",s_trans/p_gen)
print("Total Energy Consumed : ",energy_consumed)

