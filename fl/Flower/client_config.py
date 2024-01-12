import flwr as fl
import warnings
from collections import OrderedDict
from typing import List, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from datasets.utils.logging import disable_progress_bar
from torch.utils.data import DataLoader
import pandas as pd

DEVICE = "mps"

def set_parameters(net, parameters: List[np.ndarray]):
    params_dict = zip(net.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.Tensor(v) for k,v in params_dict})
    net.load_state_dict(state_dict, strict = True)

def get_parameters(net)->List[np.ndarray]:
    return [val.cpu().numpy() for _, val in net.state_dict().items()]

def train(net, trainloader, epochs:int):
	criterion = torch.nn.CrossEntropyLoss()
	optimizer = torch.optim.Adam(net.parameters())
	net.train()
	for epoch in range(epochs):
		correct, total, epoch_loss = 0, 0, 0.0
		for batch in trainloader:
			images, labels = batch["img"].to(DEVICE), batch["label"].to(DEVICE)
			optimizer.zero_grad()
			outputs = net(images)
			loss = criterion(outputs, labels)
			loss.backward()
			optimizer.step()
			# Metrics
			epoch_loss += loss
			total += labels.size(0)
			correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
		epoch_loss /= len(trainloader.dataset)
		epoch_acc = correct / total
		print(f"Epoch {epoch+1}: train loss {epoch_loss}, accuracy {epoch_acc}")

def test(net, testloader):
	criterion = torch.nn.CrossEntropyLoss()
	correct, total, loss = 0,0,0.0
	net.eval()
	with torch.no_grad():
		for batch in testloader:
			images, labels = batch["img"].to(DEVICE), batch["label"].to(DEVICE)
			outputs = net(images)
			loss += criterion(outputs, labels).item()
			_, predicted = torch.max(outputs.data, 1)
			total += labels.size(0)
			correct += (predicted == labels).sum().item()
	loss /= len(testloader.dataset)
	accuracy = correct / total
	return loss, accuracy

class FlowerClient(fl.client.NumPyClient):
	def __init__(self, net, trainloader, valloader):
		self.net = net
		self.trainloader = trainloader
		self.valloader = valloader

	def get_parameters(self, config):
		return get_parameters(self.net)

	def fit(self, parameters, config):
		set_parameters(self.net, parameters)
		train(self.net, self.trainloader, epochs=1)
		return get_parameters(self.net), len(self.trainloader), {}

	def evaluate(self, parameters, config):
		set_parameters(self.net, parameters)
		loss, accuracy = test(self.net, self.valloader)
		return float(loss), len(self.valloader), {"accuracy": float(accuracy), "loss":float(loss)}
