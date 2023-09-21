from node import node
from network import network
import networkx as nx
import numpy as np


class DIJKSTRA:
	def __init__(self):
		self.net = network()
		self.graph_data = {}
		self.sink = node(0,0,0)
		self.k = 0
		self.n = 0
		self.n_map = {}
		self.total_latency = 0
		self.round_latency = 0
		self.energy_consumed= 0
		self.message_tranmitted = 0
		self.message_generated = 0
		self.energy_for_reception = 0
		self.rounds = 0
		self.latency_history = []
		
		pass

	def load_network(self, graph_data_path, save_mode):
		"""
		save_mode: 0 -> old network data
		save_mode: 1 -> new network data
		"""
		if(save_mode == 0):
			self.net = network(500, 500, 400, 0, 0)
			self.net.initialise_nodes_fixed(1, 0.4)
			self.net.set_parameters(2000, 200, 2000, 3*1e8, 50)
			#load graph

			graph_data = np.load(graph_data_path, allow_pickle=True).item()
		else:
			_, _, graph_data = self.net.load_network_topology(graph_data_path)

		self.graph_data = graph_data
		self.sink = self.net.sink
		self.k = self.net.packet_length
		self.n = self.net.number_of_nodes
		self.n_map = self.net.node_map
		self.energy_for_reception = self.n_map[1].energy_for_reception(self.k)
		return graph_data

	def load_graph_from_ppo(self, graph_data):
		self.G = self.net.set_nxg_from_npy(graph_data)
		self.net.show_graph()
		return self.G

	def load_graph(self):
		self.G = self.net.set_nxg()
		self.net.show_graph()
		return self.G

	def weight(self, u, v):
		try:
			return self.G[u][v]['weight'] if self.G[u][v]['weight'] > self.n_map[u].current_energy else 1e9
		except:
			return 1e9

	def check_path(self, path):
		return True
		# n = len(path)
		# path_sum =0
		# for i in range(n - 1):
		# 	curr = path[i]
		# 	next = path[i+1]
		# 	path_sum += G[curr][next]['weight']
		# return path_sum < 1e9

	def run(self):
		self.dead_node = set()
		while self.G.number_of_nodes > 0.1*self.n:
			self.total_latency+= self.rnd_latency
			self.rnd_latency=0

			for i in range(1, self.n + 1):
				if i in self.dead_node:
					try:
						self.G.remove_node(i)
					except:
						continue
					continue

				curr = self.n_map[i]
				if curr.current_energy < curr.critical_energy:
					self.dead_node.add(i)
					self.G.remove_node(i)
					continue

				#active node message generation
				self.message_generated += 1
				path = self.net.findShortestPath(curr)

				# print(i, path)
				while len(path) != 0:
					next = self.net.node_map[path.pop()]
					self.round_latency+=(self.net.latency(curr,next))
					trns=curr.energy_for_transmission(self.k, next.dist(curr))
					curr.current_energy -= trns
					recep=self.energy_for_reception
					next.current_energy -= recep
					self.energy_consumed+=recep
					curr = next

				snk=curr.energy_for_transmission(self.k, curr.dist(self.net.sink))
				if curr.id == 0:
					self.message_tranmitted += 1
				elif curr.current_energy > snk:
					curr.current_energy -= snk
					self.round_latency+=(self.net.latency(curr,self.sink))
					self.energy_consumed+=snk
					self.message_tranmitted += 1
				elif curr.id == i:
					self.dead_node.add(i)
					self.G.remove_node(i)
				# message_rec_flag = 0
				# try:
				# 	path = nx.dijkstra_path(G, i, 0, weight)
				# except:
				# 	#if no paths found, try direct transmission.
				# 	if curr.energy_for_transmission(k, curr.dist(sink)) < curr.current_energy:
				# 		print("message failed!")
				# 		G.remove_node(i)
				# 		dead_node.add(i)
				# 	else:
				# 		curr.current_energy -= curr.energy_for_transmission(k, curr.dist(sink))
				# 		s_trans += 1
				# 	continue

				# # for path in paths_list:
				# 	# if check_path(path):
				# for i_id in range(len(path) - 1):
				# 	curr_node_id = path[i_id]
				# 	next_node_id = path[i_id + 1]
				# 	curr_node = n_map[curr_node_id]
				# 	next_node = n_map[next_node_id]
				# 	rnd_latency += net.latency(curr_node, next_node)
				# 	curr_node.current_energy -= G[curr_node_id][next_node_id]['weight']
				# 	next_node.current_energy -= energy_for_reception
				# 	energy_consumed += G[curr_node_id][next_node_id]['weight'] + energy_for_reception
				# print("path complete! :" , i)
				# #the message is received by sink
				# s_trans += 1
				# message_rec_flag = 1

				# #if message was not received
				# if message_rec_flag == 0:
				# 	dead_node.add(i)
				# 	G.remove_node(i)
