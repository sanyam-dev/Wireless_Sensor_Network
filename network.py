from node import node
import random
import matplotlib as plt
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
		sink = node(0, base_x, base_y,0,0)
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
			Node = node(random.randint(0,self.area_length), random.randint(0,self.area_width), i,0,0)
			Node.node_energy_setup(node_initial_energy, node_critical_energy)
			self.node_list.append(Node)
			self.node_map[i] = Node


	def initialise_nodes_fixed(self, node_initial_energy, node_critical_energy):
		x=[2, 15, 4, 46, 35, 41, 45, 46, 25, 16, 21, 18, 44, 46, 48, 0, 25, 38, 26, 19, 49, 43, 29, 3, 30, 41, 44, 35, 0, 47, 4, 46, 26, 4, 32, 29, 41, 13, 31, 38, 65, 66, 73, 62, 85, 76, 94, 73, 88, 79, 83, 78, 51, 79, 67, 62, 86, 55, 77, 82, 64, 80, 85, 61, 50, 56, 93, 65, 83, 91, 68, 57, 58, 77, 60, 78, 81, 56, 92, 97, 120, 130, 131, 108, 118, 105, 124, 123, 101, 115, 100, 115, 117, 139, 110, 116, 140, 107, 107, 103, 146, 134, 129, 122, 104, 134, 103, 104, 113, 121, 121, 150, 133, 133, 144, 147, 105, 106, 116, 149, 168, 195, 163, 178, 154, 183, 150, 173, 198, 172, 174, 165, 158, 152, 158, 196, 154, 154, 151, 197, 197, 191, 155, 184, 189, 185, 199, 159, 177, 186, 186, 176, 191, 154, 157, 176, 162, 178, 162, 194, 232, 241, 237, 203, 227, 238, 205, 219, 210, 210, 246, 221, 211, 209, 224, 208, 247, 234, 249, 228, 200, 240, 219, 245, 237, 228, 233, 203, 210, 234, 205, 237, 236, 230, 236, 205, 233, 221, 223, 242, 258, 251, 282, 275, 277, 283, 287, 270, 261, 289, 283, 270, 291, 289, 279, 254, 281, 276, 270, 261, 282, 259, 277, 264, 258, 250, 277, 271, 263, 267, 271, 254, 296, 251, 270, 292, 281, 254, 250, 258, 327, 346, 308, 333, 342, 344, 342, 329, 318, 346, 306, 303, 325, 318, 315, 334, 347, 334, 320, 335, 307, 342, 321, 339, 349, 300, 337, 333, 326, 341, 337, 304, 318, 307, 331, 322, 342, 346, 325, 347, 373, 367, 356, 369, 366, 392, 371, 400, 394, 394, 366, 375, 355, 393, 365, 388, 381, 356, 374, 353, 399, 384, 382, 379, 382, 397, 393, 359, 386, 355, 362, 376, 373, 394, 384, 379, 399, 361, 356, 369, 446, 445, 448, 446, 431, 447, 405, 423, 403, 449, 427, 439, 423, 418, 441, 447, 448, 400, 402, 420, 408, 416, 414, 425, 445, 424, 442, 406, 412, 442, 406, 416, 419, 400, 406, 422, 425, 421, 415, 433, 481, 492, 489, 450, 481, 494, 461, 454, 482, 457, 471, 453, 488, 471, 495, 469, 499, 461, 450, 454, 481, 462, 471, 450, 491, 467, 489, 484, 484, 491, 466, 467, 487, 466, 469, 455, 451, 483, 471, 494]
		y=[48, 46, 36, 28, 78, 50, 90, 84, 130, 145, 103, 122, 195, 160, 179, 154, 246, 248, 243, 223, 269, 300, 271, 282, 326, 318, 347, 335, 365, 382, 375, 383, 413, 406, 407, 406, 454, 457, 466, 454, 3, 47, 1, 42, 67, 61, 75, 73, 121, 120, 140, 120, 176, 182, 174, 150, 240, 220, 225, 203, 264, 255, 282, 250, 336, 331, 320, 318, 351, 367, 376, 358, 416, 442, 410, 429, 466, 497, 487, 496, 45, 8, 14, 47, 84, 97, 59, 56, 128, 147, 124, 116, 182, 199, 188, 158, 220, 241, 249, 201, 287, 280, 298, 291, 305, 340, 325, 308, 371, 356, 386, 355, 434, 448, 429, 425, 478, 458, 487, 459, 6, 44, 34, 5, 93, 84, 90, 87, 132, 105, 143, 115, 175, 150, 195, 198, 203, 242, 244, 233, 285, 298, 298, 255, 347, 302, 307, 312, 374, 381, 368, 391, 448, 423, 439, 423, 477, 453, 487, 470, 48, 11, 47, 45, 75, 50, 73, 56, 147, 101, 107, 126, 150, 175, 197, 190, 237, 207, 223, 227, 267, 283, 251, 281, 327, 342, 319, 346, 390, 390, 363, 372, 403, 450, 411, 445, 452, 486, 486, 461, 37, 35, 19, 19, 60, 62, 73, 100, 145, 148, 131, 111, 190, 150, 193, 179, 202, 204, 246, 206, 251, 270, 297, 267, 309, 326, 307, 348, 400, 353, 378, 377, 440, 404, 405, 401, 498, 479, 459, 483, 49, 28, 39, 9, 97, 93, 77, 98, 116, 101, 125, 129, 168, 172, 184, 183, 237, 214, 218, 247, 260, 280, 261, 290, 335, 313, 350, 316, 377, 369, 367, 353, 434, 400, 425, 426, 499, 470, 471, 461, 14, 49, 18, 16, 52, 76, 96, 82, 150, 105, 101, 128, 190, 187, 160, 165, 244, 243, 235, 201, 254, 291, 298, 253, 333, 339, 319, 340, 361, 357, 395, 372, 421, 414, 432, 410, 467, 488, 459, 452, 22, 37, 22, 29, 76, 64, 59, 61, 101, 132, 143, 133, 175, 193, 187, 188, 219, 221, 231, 239, 254, 265, 281, 276, 303, 341, 328, 319, 371, 378, 378, 391, 408, 438, 424, 444, 451, 450, 487, 457, 9, 15, 27, 14, 55, 56, 64, 92, 140, 148, 139, 135, 161, 160, 193, 159, 206, 230, 209, 247, 252, 253, 251, 285, 332, 309, 324, 339, 397, 384, 391, 361, 426, 448, 423, 442, 459, 468, 484, 491]
		
		
		self.node_map[0] = self.sink
		for i in range(1, self.number_of_nodes + 1):
			Node = node(x[i-1], y[i-1], i,0,0)
			Node.node_energy_setup(node_initial_energy, node_critical_energy)
			self.node_list.append(Node)
			self.node_map[i] = Node
		
		
		
		# self.node_map[0] = self.sink
		# p=10
		# nod=1
		
		# for x in range(1,p+1):	
		# 	for y in range(1,p+1):
		# 		for i in range(1, int((self.number_of_nodes)/(p*p))+1):
		# 			xx=random.randint(((x-1)*self.area_length)/p,(x*self.area_length)/p)
		# 			yy=random.randint(((y-1)*self.area_width)/p,(y*self.area_width)/p)
		# 			print(xx,yy )
		# 			# print(yy)
		# 			Node = node(xx, yy, nod)  
		# 			Node.node_energy_setup(node_initial_energy, node_critical_energy)
		# 			self.node_list.append(Node)
		# 			self.node_map[nod] = Node
		# 			nod+=1
		


		




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

	# def show_graph(self):
	# 	G = nx.Graph()
	# 	positions = {}
	# 	for Node in self.node_list:
	# 		# G.add_node(str(Node.id), pos = (Node.x, Node.y))
	# 		positions[Node.id] = [Node.x, Node.y]
	# 	ax = plt.figure().gca()
	# 	ax.set_axis_off()
	# 	options = {"node_size": 300, "node_color": "red"}
	# 	nx.draw(G, positions, with_labels = True, **options)
	# 	plt.show()

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


	def latency(self,curr:node,next:node)->int:
		l=0
		l+=(self.packet_length/self.transmission_rate)
		l+=(curr.dist(next)/self.transmission_speed)
		# l+=(1/(curr.queue_param-curr.processing_param))
		return l
	