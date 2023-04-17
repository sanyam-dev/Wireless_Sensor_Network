from network import network as nw

class env:
	def __init__(self) -> None:
		self.net = nw(20, 20, 14, 0, 0)
		self.net.initialise_nodes(1, 0.4)
		self.net.set_parameters(2000,200,2000,2000,8)
		self.initial_net = self.net
		self.initial_graph = self.net.get_graph()
		self.action_space = self.set_action_space()
		self.action_space_n = len(self.action_space)
		self.obs_space = self.net.get_graph()

	def set_action_space(self)->list:
		net = self.net
		mp = net.node_map
		n = net.number_of_nodes
		action_space = []
		for i in range(1, n+1):
			for j in range(i+1, n+1):
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
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten

	def get_reward(self):
		acc = self.net.get_acc(self.obs_space)
		apl = self.net.get_apl(self.obs_space)
		#Hyper-parameters
		w1 = 1
		w2 = 6
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
			return mat_flatten, reward
		print("before:", self.net.acc, self.net.apl)

		mat[n1][n2] = 1
		mat[n2][n1] = 1
		self.obs_space = mat
		reward = self.get_reward()
		print("after:", self.net.acc, self.net.apl)
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten, reward

		# li = self.action_space[action]
		# mat = self.obs_space
		# mat[li[0].id][li[1].id] = 1
		# mat[li[1].id][li[0].id] = 1
		# self.obs_space = mat
		# self.net.graph = self.obs_space
		# mat_flatten = [num for sublist in mat for num in sublist]
		# reward = self.get_reward()
		# done = self.get_done()
		# # print(mat_flatten)
		# return mat_flatten, reward



