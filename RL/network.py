import torch
from torch import nn
import torch.nn.functional as F
import numpy as np

class FeedForwardNN(nn.Module):
	def __init__(self, n_actions, input_dims, fc1_dims=256, fc2_dims=256):
		super(FeedForwardNN, self).__init__()
		self.layer1 = nn.Linear(*input_dims, fc1_dims)
		self.layer2 = nn.Linear(fc1_dims, fc2_dims)
		self.layer3 = nn.Linear(fc2_dims, n_actions)

	def forward(self, obs):
		# Convert observation to tensor if it's a numpy array
		if isinstance(obs, np.ndarray):
			obs = torch.tensor(obs, dtype=torch.float)

		activation1 = F.relu(self.layer1(obs))
		activation2 = F.relu(self.layer2(activation1))
		output = F.softmax(self.layer3(activation2))
		# tutorial:
		# output = self.layer3(activation2)
		return output

