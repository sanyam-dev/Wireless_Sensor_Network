import torch
from torch.utils.data import random_split, DataLoader
from torchvision.transforms import ToTensor, Normalize, Compose
from torchvision.datasets import MNIST

def get_mnist(data_pata: str = './data'):
	tr =  Compose(
		[
			ToTensor(), 
			Normalize((0.1307, ), (0.3081, ))
		]
	)
	trainset = MNIST(data_pata, train = True, download=True, transform=tr)
	testset= MNIST(data_pata, train = False, download=True, transform=tr)
	return trainset, testset

def prepare_dataset(num_partitions:int,
					batch_size:int,
					val_ratio: float = 0.1):
	"""
		num_partition: number of clients
		val_ratio: ratio of validation dataset
		batch_size: batch size of dataset of each client
	"""
	trainset, testset = get_mnist()

	#pathological partitioning
		#"Data heterogenity Federated Learning"

	#iid dataset:
	num_images = len(trainset)//num_partitions
	
	partition_len = [num_images] * num_partitions

	trainsets = random_split(trainset, partition_len, torch.Generator().manual_seed(42))

	##create dataloaders
	trainloaders = []
	valloaders = []
	for trainset_ in trainsets:
		num_total_ = len(trainset_)
		num_val = int(val_ratio*num_total_)
		num_train = num_total_ - num_val
		
		for_train, for_val = random_split(trainset_, [num_train,num_val], torch.Generator().manual_seed(42))
		trainloaders.append(DataLoader(for_train, batch_size, shuffle = True, num_workers =2))
		valloaders.append(DataLoader(for_val, batch_size, shuffle = False, num_workers =2))
	
	testloader = DataLoader(testset, batch_size=120)
	
	return trainloaders, valloaders, testloader


