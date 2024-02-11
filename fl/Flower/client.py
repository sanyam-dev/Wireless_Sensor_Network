import flwr as fl
from client_config import FlowerClient
from net import Net
from flwr_datasets import FederatedDataset
from torchvision.transforms import transforms
from torch.utils.data import DataLoader


NUM_CLIENTS = 1
BATCH_SIZE = 32
DEVICE = "mps"

def load_datasets():
	fds = FederatedDataset(dataset="cifar10", partitioners={'train':NUM_CLIENTS})
	def apply_transform(batch):
		transform = transforms.Compose(
			[
				transforms.ToTensor(),
				transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
			]
		)
		batch["img"] = [transform(img) for img in batch["img"]]
		return batch

	trainloaders = []
	valloaders = []

	for partition_id in range(NUM_CLIENTS):
		partition = fds.load_partition(partition_id, "train")
		partition = partition.with_transform(apply_transform)
		partition = partition.train_test_split(train_size = 0.8)
		trainloaders.append(DataLoader(partition["train"], batch_size=BATCH_SIZE))
		valloaders.append(DataLoader(partition["test"], batch_size=BATCH_SIZE))

	testset = fds.load_full("test").with_transform(apply_transform)
	testloader = DataLoader(testset, batch_size=BATCH_SIZE)
	return trainloaders, valloaders, testloader



if __name__ == "__main__":
	trainloaders, valloaders, testloader = load_datasets()
	cid = 0
	print(cid)
	net = Net().to(device=DEVICE)
	trainloader = trainloaders[int(cid)]
	valloader = valloaders[int(cid)]
	fl.client.start_numpy_client(
		server_address="0.0.0.0:8080",
		client= FlowerClient(net, trainloader, valloader)
	)