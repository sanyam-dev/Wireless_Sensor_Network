import flwr as fl
import numpy as np
from net import Net
from typing import List, OrderedDict
import torch

def weighted_average(metrics):
	print(metrics)
	accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
	losses = [num_examples * m["loss"] for num_examples, m in metrics]
	examples = [num_examples for num_examples, _ in metrics]
	return {"accuracy": sum(accuracies) / sum(examples), "loss": sum(losses) / sum(examples)}

net = Net().to(device="mps")

class SaveModelStrategy(fl.server.strategy.FedAvg):
    def aggregate_fit(
        self,
        server_round,
        results,
        failures,
    ):
        """Aggregate model weights using weighted average and store checkpoint"""

        # Call aggregate_fit from base class (FedAvg) to aggregate parameters and metrics
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)

        if aggregated_parameters is not None:
            print(f"Saving round {server_round} aggregated_parameters...")

            # Convert `Parameters` to `List[np.ndarray]`
            aggregated_ndarrays: List[np.ndarray] = fl.common.parameters_to_ndarrays(aggregated_parameters)

            # Convert `List[np.ndarray]` to PyTorch`state_dict`
            params_dict = zip(net.state_dict().keys(), aggregated_ndarrays)
            state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
            net.load_state_dict(state_dict, strict=True)

            # Save the model
            torch.save(net.state_dict(), f"model_round_{server_round}.pth")

        return aggregated_parameters, aggregated_metrics

if __name__ == "__main__":
	strategy = SaveModelStrategy(
		fraction_fit=1.0,  # Sample 100% of available clients for training
		fraction_evaluate=1.0,  # Sample 5% of available clients for evaluation
		min_fit_clients=1,  # Never sample less than 10 clients for training
		min_evaluate_clients=1,  # Never sample less than 5 clients for evaluation
		min_available_clients=1,  # Wait until all 10 clients are available
		evaluate_metrics_aggregation_fn=weighted_average,
	)

	fl.server.start_server(
		server_address="0.0.0.0:8080",
		strategy=strategy,
		config=fl.server.ServerConfig(num_rounds=10)
	)