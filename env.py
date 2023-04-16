from network import network as nw

class env:
	def __init__(self) -> None:
		self.net = nw(20, 20, 14, 0, 0)
		self.net.initialise_nodes(1, 0.4)
		self.net.set_parameters(2000,200,2000,2000,8)
		self.reset_net = self.net
		# self.net.show_network()
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

	def get_observation_space_shape(self):
		mat = self.observation_space
		mat_flatten = [num for sublist in mat for num in sublist]
		return len(mat_flatten)

	def find_observation_space(self):
		mat = self.net.get_graph()
		return mat

	def reset(self):
		self.net = self.reset_net
		self.observation_space = self.find_observation_space()
		mat = self.observation_space
		mat_flatten = [num for sublist in mat for num in sublist]
		return mat_flatten

	def get_reward(self):
		acc = self.net.get_acc()
		apl = self.net.get_apl()
		#Hyper-parameters
		w1 = 1
		w2 = 1
		reward = w1*acc + w2*(1/apl)
		
		return reward


	def get_done(self):
		#	node energy = 0

		pass

	def step(self, action):
		li = self.action_space[action]
		# action = argmax(action)
		mat = self.observation_space
		print("current state of graph ", mat[li[0].id][li[1].id], "apl ",  self.net.apl, "acc ", self.net.acc)
		mat[li[0].id][li[1].id] = 1
		mat[li[1].id][li[0].id] = 1
		self.observation_space = mat

		mat_flatten = [num for sublist in mat for num in sublist]

		reward = self.get_reward()
		done = self.get_done()

		return mat_flatten, reward



