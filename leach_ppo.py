import numpy as np
from network import *
import random

class Leach:
	def __init__(self) -> None:
		#initialise network:
		net = network(500, 500, 400, 0, 0)
		self.net = net
		#initialise network
		graph_data_path = "results/result39/0-graph_data.npy"
		# graph_data_path = "results/result88/7-graph_data.npy"
		# graph_data_path = "results/network_data/network1network_data.npy"

		self.graph_data= self.load_network(self, graph_data_path, 0)
		self.sink = self.net.sink
		self.k = self.net.packet_length
		self.rnds = 0
		self.n = self.net.number_of_nodes
		self.n_map = self.net.node_map
		self.latency_per_round = list()
		self.energy_consumed_per_round = list()
		self.throughput_per_round = list()
		self.P = 0.04


	def load_network(self, graph_data_path, save_mode):
		"""
		save_mode: 0 -> old network data
		save_mode: 1 -> new network data
		"""
		if(save_mode == 0):
			self.net.initialise_nodes_fixed(1, 0)
			self.net.set_parameters(2000, 8, 2000, 3*1e8, 50)
			#load graph

			graph_data = np.load(graph_data_path, allow_pickle=True).item()
		else:
			_, _, graph_data = self.net.load_network_topology(graph_data_path)

		return graph_data



	def run(self):
		net = self.net
		sink = self.sink
		P = self.P
		not_cluster_heads = set(i for i in range(1, self.n + 1))
		failed_iter = 0
		rnd_latency = 0

		dead_nodes = set()


		for N in net.node_list:
			N.dist(sink)
			N.setup_for_leach()


		round_number = 0
		active_nodes = self.n
		while len(dead_nodes) <= 0.9*self.n:
			#every loop is one unit of time

			rnd_latency = 0
			round_number += 1
			round_wise_cluster_head = []

			for Node in net.node_list:

				Node.role =0

				if Node.critical_energy > Node.current_energy:
					active_nodes -= 1
					dead_nodes.append(Node)
					net.node_list.remove(Node)
					pass

				if(round_number - Node.last_head_rnd > int(1/P)):
					not_cluster_heads.add(Node.id)


			for id in not_cluster_heads:
				Tn =  P/(1 - P*(round_number % int(1/P)))
				response = round(random.uniform(0,1), 2)

				if response < Tn:
					Node.role = 1
					Node.times_elected += 1
					Node.last_head_rnd = round_number
					not_cluster_heads.remove(Node.id)
					round_wise_cluster_head.append(Node)

			print(len(round_wise_cluster_head))






