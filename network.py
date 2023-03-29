import random
import matplotlib.pyplot as plt
from node import *
import networkx as nx

class network:
	"""
	initialises the network

	parameters:
	-	Length
	-	Width
	-	number of nodes
	-	x coordinate of BS
	-	y coordinate of BS
	"""
	def __init__(self, area_length, area_width, nodes, base_x, base_y) -> None:
		self.area_length = area_length
		self.area_width = area_width
		self.number_of_nodes = nodes
		self.base_station_x = base_x
		self.base_station_y = base_y
		self.node_list = []
		self.node_map = {}

		#	For Dijkstra
		self.adj_mat = {}
		self.node_shortest_path = {}


	def initialise_nodes(self, node_initial_energy, node_critical_energy):
		"""
		add nodes the network

		parameters:
		-	Node initial energy
		-	Node critical energy
		"""
		for i in range(1, self.number_of_nodes + 1):
			Node = node(random.randint(0,self.area_length), random.randint(0,self.area_width), i)
			Node.node_energy_setup(node_initial_energy, node_critical_energy)
			self.node_list.append(Node)
			self.node_map[i] = Node


	def set_parameters(self,dist_para, len_of_packets,
		    transmission_rate, speed_of_transmission,
		    radio_distance
			):
		"""
		set network parameters

		parameters:
		-	Distribution parameter
		-	Length of Packets
		-	Transmission rate
		-	Speed of Transmission
		-	Limit of radio distance
		"""
		self.distribution_parameters = dist_para
		self.packet_length = len_of_packets	#bits
		self.transmission_rate = transmission_rate	#kbps
		self.transmission_speed = speed_of_transmission	#m/s
		self.radio_distance = radio_distance

	def show_network(self):
		"""
		displays the network
		"""
		x=[]
		y=[]
		for	Node in self.node_list:
			if(Node.current_energy >= Node.critical_energy):
				x.append(Node.x)
				y.append(Node.y)

		plt.xlim(-1, self.area_length)
		plt.ylim(-1, self.area_width)
		plt.scatter(x,y, marker='x')
		plt.scatter(self.base_station_x,self.base_station_y, c="red")
		# for Node in self.node_list:
		# 	plt.text(Node.x+.03, Node.y+.03, Node.id, fontsize = 6)

		plt.show()

	def show_graph(self):
		G = nx.Graph()
		positions = {}
		for Node in self.node_list:
			# G.add_node(str(Node.id), pos = (Node.x, Node.y))
			positions[Node.id] = [Node.x, Node.y]
		ax = plt.figure().gca()
		ax.set_axis_off()
		options = {"node_size": 300, "node_color": "red"}
		nx.draw(G, positions, with_labels = True, **options)
		plt.show()

	def network_adj_matrix(self) -> dict:
		"""
		returns an adjacency matrix of the network

		``` 0 is the sink node```
		"""
		adj = {}
		for i in self.node_list:
			nn = []
			for j in self.node_list:
				if	j == i:
					continue
				x = i.dist_from_node(j)
				if x <= self.radio_distance:
					nn.append([j, x])
			adj[i.id] = nn

		nn = []
		for Node in self.node_list:
			x = Node.dist_from_server([self.base_station_x, self.base_station_y])
			if x <= self.radio_distance:
				nn.append([Node, x])
			adj[0] = nn

		self.adj_mat = adj
		return adj


	def dijkstra(self)-> dict:
		"""
			Returns a dictionary where every node
			is mapped to the list containing shortest path
			found via Dijkstra's algorithm
		"""

		dp = [self.area_length*5 for _ in range(self.number_of_nodes + 1)]
		q = []
		node_path = []

		# Taking b.s as source node
		dp[0] = 0
		node_path[0] = -1
		q.append(0)

		while len(q) != 0:
			x = q.pop(0)
			if x != int(0):
				x = x.id
			nn = self.adj[x]
			for i in nn:
				if	dp[i[0].id] > dp[x] + i[1]:
					dp[i[0].id] = round(dp[x] + i[1], 2)
					q.append(i[0])
					node_path[i[0].id] = x

			shortest_paths = {}
			for Node in self.node_list:
				path = []
				currNode = Node
				while currNode != int(-1):
					currNode = self.node_map[node_path[currNode.id]]
					path.append(currNode)

				shortest_paths[Node] = path
				