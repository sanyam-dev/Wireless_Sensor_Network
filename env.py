from network import network as nw
import networkx as nx
import matplotlib.pyplot as plt

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
		self.apl = 9999
		self.acc = 0

	def set_nxg(self):
		G = nx.Graph()
		graph = self.net.get_graph()
		mp = self.net.node_map
		for i in range(1,len(graph)):
			G.add_node(i, pos = (mp[i].x, mp[i].y))
		G.add_node(0, pos = (0, 0))
		for i in range(len(graph)):
			for j in range(len(graph)):
				if graph[i][j] == 1:
					G.add_edge(i, j, color = 'black')
		self.apl = round(nx.average_shortest_path_length(G), 3)
		self.acc = round(nx.average_clustering(G), 3)
		return G


	def set_action_space(self)->list:
		net = self.net
		mp = net.node_map
		n = net.number_of_nodes
		action_space = []
		for i in range(1, n+1):
			for j in range(i+1, n+1):
				if net.graph[i][j] == 0 and mp[i].dist(mp[j]) <= 0.6*net.area_length and mp[i].dist(mp[j]) >= 0.25*net.area_length:
					action_space.append([mp[i], mp[j]])
		return action_space

	def get_observation_space_shape(self):
		mat = self.obs_space
		mat_flatten = [num for sublist in mat for num in sublist]
		return len(mat_flatten)


	def set_observation_space(self):
		mat = self.net.get_graph()
		return mat

	def reset(self):
		self.net = self.initial_net
		self.obs_space = self.initial_graph
		mat = self.obs_space
		self.edges_added = []
		self.nxg = self.set_nxg()
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten

	def get_reward(self):
		acc = self.acc
		apl = self.apl
		#Hyper-parameters
		w1 = 10
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
		if mat[n1][n2] == 1:
			reward = 0
			mat_flatten = [num for sublist in mat for num in sublist]
			# print("before:", self.net.acc, self.net.apl)
			# print("after:", self.net.acc, self.net.apl)
			return mat_flatten, reward
		print("before:", self.acc, self.apl)
		self.edges_added.append([n1, n2])
		mat[n1][n2] = 1
		mat[n2][n1] = 1
		G = self.nxg
		for edge in self.edges_added:
			G.add_edge(edge[0], edge[1], color = 'red')
		self.apl = round(nx.average_shortest_path_length(G), 3)
		self.acc = round(nx.average_clustering(G), 3)
		self.obs_space = mat
		reward = self.get_reward()
		print("after:", self.acc, self.apl)
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten, reward

	def show_graph(self):
		G = self.nxg
		pos = nx.get_node_attributes(G, 'pos')
		e = G.edges()
		n_color = ['red' if node == 0 else 'blue' for node in G]
		e_color =  [G[u][v]['color'] for u,v in e]
		plt.figure(2, figsize=(12, 8))
		nx.draw(G, pos, node_color = n_color,
	  				edge_color = e_color, with_labels = True)

		plt.show()

