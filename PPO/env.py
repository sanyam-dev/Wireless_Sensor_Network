from network import network as nw
from torch import argmax

class env:
	def __init__(self) -> None:
		self.net = nw(500, 500, 300, 0, 0)
		self.net.initialise_nodes(1, 0.2)
		self.net.set_parameters(2000,200,2000,2000, 30)
		self.reset_net = self.net
		self.net.show_network()
		self.action_space = self.find_action_space()
		self.action_space_n = len(self.action_space)
		self.observation_space = self.find_observation_space()

	def find_action_space(self)->list:
		net = self.net
		mp = net.node_map
		n = net.number_of_nodes
		action_space = []
		for i in range(1, n+1):
			for j in range(i+1, n+1):
				action_space.append([mp[i], mp[j]])
		return action_space

	def get_observation_space_shape(self)->list:
		obs = self.observation_space
		res = []
		for i in obs:
			for j in i:
				res.append[j]

		return res

	def find_observation_space(self)->list:
		n = self.net.number_of_nodes
		li = self.net.node_list
		adj_mat = [[0 for _ in range(n+1)] for _ in range(n+1)]
		for i in range(n+1):
			for j in range(i+1, n+1):
				if li[i].dist(li[j])  < self.net.radio_distance:
					adj_mat[i][j] = 1
					adj_mat[j][i] = 1
		return adj_mat

	def reset(self):
		self.net = self.reset_net
		self.observation_space = self.find_observation_space()
		return self.observation_space

	def get_reward(self):
		acc = self.net.get_acc()
		apl = self.net.get_apl()
		#Hyper-parameters
		w1 = 1
		w2 = 1
		return w1*acc + w2*(1/apl)


	def get_done(self):
		#	node energy = 0

		pass

	def step(self, action):
		action = argmax(action)
		action = self.action_space(action)
		mat = self.observation_space
		mat[action[0]][action[1]] = 1
		mat[action[1]][action[0]] = 1
		reward = self.get_reward()
		done = self.get_done()
		self.observation_space = mat

		return mat, reward, done



