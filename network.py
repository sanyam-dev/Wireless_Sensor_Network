from node import *
import random
import matplotlib.pyplot as plt
import networkx as nx
import heapq as pq

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
		self.node_list = []

		# self.node_map = {int: node.}
		self.node_map = {}
		sink = node(0, base_x, base_y)
		sink.node_energy_setup(5*1e9, -5*1e9)
		self.sink = sink
		self.radio_distance = 0

	def initialise_nodes(self, node_initial_energy, node_critical_energy):
		"""
		add nodes the network

		parameters:
		-	Node initial energy
		-	Node critical energy
		"""
		self.node_map[0] = self.sink
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
		self.radio_distance = radio_distance	#m

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
		plt.scatter(0,0, c="red")
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

	def set_nnd(self)-> list:
		nnd = []
		for i in range(1, self.number_of_nodes + 1):
			currNode = self.node_map[i]
			if currNode.dist(self.sink) <= self.radio_distance:
				nnd.append([self.sink, currNode, currNode.dist(self.sink)])

			for j in range(i + 1, self.number_of_nodes + 1):
				tmpNode = self.node_map[j]
				x = tmpNode.dist(currNode)
				nnd.append([currNode, tmpNode, x])
		# self.nnd = nnd
		return nnd

	def network_adj_matrix(self) -> dict:
		"""
		returns an adjacency matrix of the network

		``` 0 is the sink node```
		"""

		adj = {}
		nnd = self.set_nnd()
		for i in range(self.number_of_nodes + 1):
			adj[i] = []
		for n1, n2, x in nnd:
			if x <= self.radio_distance:
				adj[n1.id].append([n2.id, x])
				adj[n2.id].append([n1.id, x])
		# self.adj = adj
		return adj


	def dijkstra(self)->list:
		"""
			Returns a dictionary where every node
			is mapped to the list containing shortest path
			found via Dijkstra's algorithm
		"""
		path = [[0, self.node_map[i].dist(self.sink)] for i in range(self.number_of_nodes + 1)]
		unvisited_nodes = {i for i in range(self.number_of_nodes + 1)}
		G = self.network_adj_matrix()
		dist = [int(1e9) for _ in range(self.number_of_nodes + 1)]
		#	sink is the source node
		dist[0] = 0
		li = [0]
		while len(li) != 0:
			currNode = pq.heappop(li)
			if currNode not in unvisited_nodes: continue
			unvisited_nodes.remove(currNode)

			for n,x in G[currNode]:
				if dist[n] > dist[currNode] + x and n in unvisited_nodes:
					dist[n] = dist[currNode] + x
					path[n] = [currNode, x]
					pq.heappush(li, n)
		print(path)
		return path

	def findShortestPath(self, curr):
		"""
			Returns the smallest possible path from current node
			to sink

			parameters:
				-	node
		"""
		adj = {int: list}
		n = self.number_of_nodes
		r = self.radio_distance

		for i in range(n + 1):
			x = self.node_map[i]
			adj[i] = []
			if not x.is_functional():
				continue
			for j in range(i+1, n+1):
				y = self.node_map[j]
				if not y.is_functional():
					continue
				d = x.dist(y)
				adj[j] = []
				if d < r and y.current_energy > y.energy_for_reception(self.packet_length):
					adj[i].append([j, d])
					adj[j].append([i, d])

		u_n = {i for i in range(self.number_of_nodes + 1)} #unvisited nodes
		dist = [int(1e9) for _ in range(self.number_of_nodes + 1)]
		path = [-1 for _ in range(n+1)]
		q = [0]
		while len(q) != 0:
			x = pq.heappop(q)
			if x not in u_n:
				continue
			u_n.remove(x)
			nn = adj[x]
			for y,d in nn:
				if d + dist[x] < dist[y]:
					pq.heappush(q,y)
					dist[y] = d + dist[x]
					path[y] = x

		# if path[curr.id] != -1:
		li = []
		c = path[curr.id]
		while c != -1:
			li.append(c)
			c = path[c]

		if len(li) != 0:
			return li

		st = [curr.id]
		while not len(st) == 0:
			i = st.pop()
			nn = adj[i]
			if i != curr.id:
				li.append(i)
			c = self.node_map[i]
			dx = c.dist(self.sink)
			for j,d in nn:
				p = self.node_map[j].dist(self.sink)
				if p < dx:
					dx = p
					st.append(j)
					path[i] = j

		return li