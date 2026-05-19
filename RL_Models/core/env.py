from RL_Models.core.network import network as nw
import networkx as nx
import matplotlib.pyplot as plt
import os
import numpy as np
import copy

class env:
	def __init__(self) -> None:
		self.net = nw(500, 500, 400, 0, 0)
		# self.net.initialise_nodes_fixed(1, 0.4)
		# self.net.set_parameters(2000,200,2000,2000,50)
		_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "network1network_data.npy")
		self.net.load_network_topology(_config_path)
		self.initial_net = self.net
		self.initial_graph = self.net.get_graph()
		self.action_space = self.set_action_space()
		# self.action_space = self.set_action_space_server()
		# self.action_space = self.set_action_space_dist()
		self.action_space_n = len(self.action_space)
		self.edges_added = []
		self.action_added = []
		self.obs_space = self.initial_graph
		self.graph = self.obs_space
		self.nxg = self.set_nxg()
		self.init_nxg = copy.deepcopy(self.nxg)
		# self.apl = 9999
		# self.acc = 0
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
		graph_data = {
			'edges': list(self.nxg.edges()),
			'edges_color': list(self.edge_color)
		}
		try:
			np.save(path +'/'+ str(i) + '-graph_data.npy', graph_data)
		except:
			os.makedirs(path)
			np.save(path +'/'+ str(i) + '-graph_data.npy', graph_data)
		print("graph .npy saved : " + path)
		# self.net.save_network(path+'/network/' + str(i))

	def set_action_space(self)->list:
		mp = self.net.node_map
		n = self.net.number_of_nodes
		action_space = []
		for i in range(1, n+1):
			for j in range(i+1, n+1):
				if self.net.graph[i][j] == 0:
					action_space.append([mp[i], mp[j]])
		return action_space

	def set_action_space_dist(self)->list:
		mp = self.net.node_map
		n = self.net.number_of_nodes
		action_space = []
		dm = self.net.calculate_dist()
		l = min(self.net.area_length, self.net.area_width)
		for i in range(1, n-1):
			for j in range(i+1, n):
				if dm[i][j] <= 0.5*l and dm[i][j] >= 0.25*l:
					action_space.append([mp[i], mp[j]])
		return action_space

	def set_action_space_server(self)->list:
		mp = self.net.node_map
		n = self.net.number_of_nodes
		action_space = []
		for i in range(1,n+1):
			if self.net.graph[i][0] == 0:
				action_space.append([mp[i], mp[0]])
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
		self.net = copy.deepcopy(self.initial_net)
		self.obs_space = copy.deepcopy(self.initial_graph)
		self.edges_added = []
		self.action_added = []
		self.action_space = self.set_action_space()
		self.action_space_n = len(self.action_space)
		self.nxg = self.set_nxg()
		self.init_nxg = copy.deepcopy(self.nxg)
		mat = self.obs_space
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten

	def get_reward(self, edge_repeat):
		if edge_repeat == 1:
			return -10
		acc = self.acc
		apl = self.apl
		w1 = 1
		w2 = 1
		reward = w1*acc + w2*(1/apl)
		reward = round(reward, 3)
		return reward

	def get_done(self):
		if self.action_space_n == 0:
			return True
		return False

	def step(self, action):
		li = self.action_space[action]
		n1 = li[0].id
		n2 = li[1].id
		mat = self.obs_space
		edge_repeat = 1 if [n1, n2] in self.edges_added else 0
		self.edges_added.append([n1, n2])
		self.edges_added.append([n2, n1])
		mat[n1][n2] = 1
		mat[n2][n1] = 1
		self.nxg.add_edge(n1, n2, color='red')
		self.apl = round(nx.average_shortest_path_length(self.nxg), 3)
		self.acc = round(nx.average_clustering(self.nxg), 3)
		self.obs_space = mat
		self.action_space.pop(action)
		self.action_space_n = len(self.action_space)
		reward = self.get_reward(edge_repeat)
		done = self.get_done()
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten, reward, done, {}

	def save_graph(self, path, i):
		G = self.nxg
		pos = nx.get_node_attributes(G, 'pos')
		e = G.edges()
		n_color = ['red' if node == 0 else 'blue' for node in G]
		e_color =  [G[u][v]['color'] for u,v in e]
		self.edge_color = e_color
		plt.figure(2, figsize=(12, 8))
		nx.draw(G, pos, node_color = n_color, node_size = 60,
			edge_color = e_color, with_labels = True, font_color = "green")
		f = "episode" + str(i)
		path = os.path.join(path, f)
		try:
			plt.savefig(path)
			plt.clf()
		except:
			os.makedirs(path)
			plt.savefig(path)
			plt.clf()

		# plt.show()

	def reset_to_copy(self, env1):
		self.reset()
		for edge in env1.action_added:
			self.add(edge)


	def add(self, action):
		# print("action",action)
		u = action[0].id
		v = action[1].id
		self.obs_space[u][v] = 1
		self.obs_space[v][u] = 1
		self.nxg.add_edge(u, v, color = 'red')
		try:
			self.action_space.remove(action)
		except ValueError:
			pass
		self.action_space_n = len(self.action_space)
		self.action_added.append(action)
