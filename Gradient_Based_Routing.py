from node import *
from network import *

net = network(100, 100, 40, 0, 0)
net.set_parameters(2000,2000,2000,2000, 30)
net.initialise_nodes(1, 0.2)

net.set_nnd()
INF = int(1e9)

sink = [net.base_station_x, net.base_station_y]
