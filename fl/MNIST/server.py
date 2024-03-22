from omegaconf import DictConfig
from model import Net, test
import torch
from collections import OrderedDict
from pathlib import Path

def get_on_fit_config_fn(config: DictConfig):
	def on_fit_config_fn(server_round: int):
		return {'lr':config.lr, 'momentum':config.momentum, 'local_epochs':config.local_epochs}

	return on_fit_config_fn

def get_evaluate_fn(num_classes, testloader, save_config):
	
	def evaluate_fn(server_round: int, parameters,config):
		model = Net(num_classes)
		device= torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
		params_dict = zip(model.state_dict().keys(), parameters)
		state_dict = OrderedDict({k: torch.Tensor(v) for k, v in params_dict})
		model.load_state_dict(state_dict, strict=True)
		#save model state
		model_name = 'model.pkl'
		result_path = Path(save_config['save_path'])/model_name
		torch.save(model.state_dict(), result_path)
		#loss & accuracy of global model 
		loss, accuracy = test(model, testloader, device)
		return loss, {'accuracy':accuracy}
			
	

	return evaluate_fn