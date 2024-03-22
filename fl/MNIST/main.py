import pickle
import hydra
from hydra.core.hydra_config import HydraConfig
from pathlib import Path
from omegaconf import DictConfig, OmegaConf
from dataset import prepare_dataset
from client import generate_client_fn
from server import get_on_fit_config_fn, get_evaluate_fn
import flwr as fl

@hydra.main(config_path="conf", config_name="base", version_base=None)
def main(cfg: DictConfig):
	print(OmegaConf.to_yaml(cfg))
	
	#prepare dataset
	trainloaders, valloaders, testloader = prepare_dataset(cfg.num_clients, cfg.batch_size)	
	print("trainloaders: ", len(trainloaders), "len of 1 trainloader: ", len(trainloaders[0]), "testloader: ", len(testloader))
	#Define Clients
	client_fn = generate_client_fn(trainloaders, valloaders, cfg.num_classes)
	
	#Define strategy
	save_path = HydraConfig.get().runtime.output_dir
	save_config = {
		'save_path' : save_path
	}
	strategy = fl.server.strategy.FedAvg(fraction_fit=0.00001,
									  min_fit_clients=cfg.num_clients_per_round_fit,
									  fraction_evaluate=0.00001,
									  min_evaluate_clients=cfg.num_clients_per_round_eval,
									  min_available_clients= cfg.num_clients,
									  on_fit_config_fn=get_on_fit_config_fn(cfg.config_fit),
									  evaluate_fn=get_evaluate_fn(cfg.num_classes, testloader, save_config))
	
	## run simulations
	history = fl.simulation.start_simulation(
		client_fn=client_fn,
		num_clients = cfg.num_clients,
		config = fl.server.ServerConfig(num_rounds=cfg.num_rounds),
		strategy = strategy
	)
	
	##save the results
	
	results_path = Path(save_path)/'results.pkl'
	results = {'history':history}
	with open(str(results_path), "wb") as f:
		pickle.dump(results, f, protocol = pickle.HIGHEST_PROTOCOL)
	
if __name__ == "__main__":
	main()