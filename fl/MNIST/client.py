from collections import OrderedDict
from typing import Dict, Tuple

from flwr.common import NDArrays, Scalar
from model import Net, train, test
import flwr as fl
import torch

class FlowerClient(fl.client.NumPyClient):
	def __init__(self, 
				trainloader, 
				valloader,
				num_class):
		super().__init__()
		
		self.trainloader = trainloader
		self.valloader = valloader
		self.model = Net(num_class)
		self.device = torch.device("mps")
	
	def set_parameters(self, parameters):
		""" 
		parameters: List of Numpy Arrays, provided by the server
		"""
		params_dict = zip(self.model.state_dict().keys(), parameters)
		state_dict = OrderedDict({k: torch.Tensor(v) for k, v in params_dict})
		self.model.load_state_dict(state_dict, strict=True)
		
		
	def fit(self, parameters, config):
		
		#copy parameters set by the server to client model
		self.set_parameters(parameters=parameters)
		lr = config['lr']
		momentum = config['momentum']
		epochs = config['local_epochs']
		optimizer = torch.optim.SGD(self.model.parameters(), lr, momentum)
		
		#Train model locally
		train(self.model, self.trainloader, optimizer, epochs, self.device)
		
		return self.get_parameters({}), len(self.trainloader), {}
		#matrix: additional info to send to the server
		
		
	def get_parameters(self, config: Dict[str, Scalar]) -> NDArrays:
		return [val.cpu().numpy() for _, val in self.model.state_dict().items()]
	
	def evaluate(self, parameters: NDArrays, config: Dict[str, Scalar]):
		#evaluate global model on evaluation dataset of the client
		self.set_parameters(parameters)
		loss, accuracy = test(self.model, self.valloader, self.device)
		return float(loss), len(self.valloader), {'accuracy': accuracy}
		

def generate_client_fn(trainloaders, valloaders, num_classes):
#spawn clients

	def client_fn(cid: str):
			
		return FlowerClient(trainloader=trainloaders[int(cid)], 
					  valloader=valloaders[int(cid)], 
					  num_class=num_classes)
	
	
	return client_fn