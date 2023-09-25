import networkx as nx
import numpy as np
from node import *
from network import *

#initialise network
net = network(500, 500, 400, 0, 0)
net.initialise_nodes(1, 0)
