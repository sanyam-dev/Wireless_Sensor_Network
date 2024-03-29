from network import network as nw
import networkx as nx
import matplotlib.pyplot as plt
import os
import numpy as np


class env:
	def __init__(self) -> None:
		self.net = nw(500, 500, 400, 0, 0)
		self.net.initialise_nodes_fixed(1, 0.4)
		self.net.set_parameters(2000,200,2000,2000,50)
		self.initial_net = self.net
		self.initial_graph = self.net.get_graph()
		self.action_space = self.set_action_space()
		self.action_space_n = len(self.action_space)
		self.edges_added = []
		self.obs_space = self.net.get_graph()
		self.nxg = self.set_nxg()
		self.init_nxg = self.nxg
		self.apl = 9999
		self.acc = 0
		self.latency = -1
		self.throughput = -1
		self.energy_consumed = -1

	def set_nxg(self):
		G = nx.Graph()
		mp = self.net.node_map
		for i in range(1,self.net.number_of_nodes + 1):
			G.add_node(i, pos = (mp[i].x, mp[i].y))
		G.add_node(0, pos = (0, 0))
		for i in range(self.net.number_of_nodes + 1):
			for j in range(self.net.number_of_nodes + 1):
				if i == j:
					continue
				if mp[i].dist(mp[j]) <= self.net.radio_distance:
					G.add_edge(i, j, color = 'black')
		self.apl = round(nx.average_shortest_path_length(G), 3)
		self.acc = round(nx.average_clustering(G), 3)
		return G

	def save_graph_npy(self, path, i):
		adj_matrix = nx.to_numpy_array(self.nxg)
		np.save(path +'/'+ str(i) + '-graph_data.npy', adj_matrix)
		print("graph .npy saved : " + path)

	def set_action_space(self)->list:
		mp = self.net.node_map
		n = self.net.number_of_nodes
		action_space = []
		for i in range(1, n+1):
			for j in range(i+1, n+1):
				if self.net.graph[i][j] == 0:
					action_space.append([mp[i], mp[j]])
		return action_space

	def get_observation_space_shape(self):
		mat = self.obs_space
		# mat_flatten = [num for sublist in mat for num in sublist]
		mt2 = []
		for i in range(len(self.obs_space)):
			for j in range(len(self.obs_space)):
				mt2.append(self.obs_space[i][j])
		# if(mt2 == mat_flatten):
		# 	print("could change obs space shape")
		return len(mt2)

	def flatten_obs_sp(self):
		mat = self.obs_space
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten

	def set_observation_space(self):
		mat = self.net.get_graph()
		return mat

	def reset(self):
		self.net = self.initial_net
		self.graph = self.net.get_graph()
		self.obs_space = self.initial_graph
		mat = self.obs_space
		self.edges_added = []
		self.nxg = self.set_nxg()
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten

	def get_reward(self, acc1, apl1):
		acc = self.acc
		apl = self.apl
		#Hyper-parameters
		w1 = 1
		w2 = 1
		reward = w1*acc + w2*(1/apl)
		reward = round(reward, 3)
		return reward


	def get_done(self):
		#	node energy = 0
		pass


	def step(self, action):
		li = self.action_space[action]
		n1 = li[0].id
		n2 = li[1].id
		mat = self.obs_space
		reward = 0
		if [n1, n2] in self.edges_added:
			print("repeat: ", n1, n2, end = " ")
			# reward = 0
			# mat_flatten = [num for sublist in mat for num in sublist]
			# # print("before:", self.net.acc, self.net.apl)
			# # print("after:", self.net.acc, self.net.apl)
			# return mat_flatten, reward
		print("before:", self.acc, self.apl, n1, n2)
		acc1 = self.acc
		apl1= self.apl
		self.edges_added.append([n1, n2])
		self.edges_added.append([n2, n1])
		mat[n1][n2] = 1
		mat[n2][n1] = 1
		G = self.nxg
		for edge in self.edges_added:
			G.add_edge(edge[0], edge[1], color = 'red')
		self.apl = round(nx.average_shortest_path_length(G), 3)
		self.acc = round(nx.average_clustering(G), 3)
		# self.latency, self.throughput, self.energy_consumed = calculateVariables(G)
		self.obs_space = mat
		reward = self.get_reward(acc1, apl1)
		print("after:", self.acc, self.apl)
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten, reward

	def save_graph(self, path, i):
		G = self.nxg
		pos = nx.get_node_attributes(G, 'pos')
		e = G.edges()
		n_color = ['red' if node == 0 else 'blue' for node in G]
		e_color =  [G[u][v]['color'] for u,v in e]
		plt.figure(2, figsize=(12, 8))
		nx.draw(G, pos, node_color = n_color, node_size = 60,
	  				edge_color = e_color, with_labels = False)
		f = "episode" + str(i)
		path = os.path.join(path, f)
		plt.savefig(path)
		plt.clf()
		# plt.show()

