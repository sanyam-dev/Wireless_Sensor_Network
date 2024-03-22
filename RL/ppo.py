from network import FeedForwardNN

class PPO:
	def __init__(self, env):
		self.env = env
		self.obs_dim = env.observation_space.shape[0]
		self.act_dim = env.action_space.shape[0]
		self.actor = FeedForwardNN(self.obs_dim, self.act_dim)
		self.critic = FeedForwardNN(self.obs_dim, 1)
		self._init_hyperparameters()

	def _init_hyperparameters(self):
		# Default values for hyperparameters, will need to change later.
		self.timesteps_per_batch = 4800            # timesteps per batch
		self.max_timesteps_per_episode = 1600      # timesteps per episode

	def rollout(self):
		# Batch data
		batch_obs = []             # batch observations
		batch_acts = []            # batch actions
		batch_log_probs = []       # log probs of each action
		batch_rews = []            # batch rewards
		batch_rtgs = []            # batch rewards-to-go
		batch_lens = []            # episodic lengths in batch

		obs = self.env.reset()
		done = False
		for ep_t in range(self.max_timesteps_per_episode):
			action = self.env.action_space.sample()
			obs, rew, done, _ = self.env.step(action)
			

	def learn(self, total_timesteps):
		timesteps_so_far = 0

		while timesteps_so_far < total_timesteps:


			#increment current timestep
			timesteps_so_far += 1