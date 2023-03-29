import math

class node:
	"""
	initialises the node

	parameters:
	-	x coordinate of node
	-	y coordinate of node
	-	node id
	"""
	def	__init__(self, x, y, id) -> None:
		self.x = x
		self.y = y
		self.id = id
		self.critical_energy = 0
		self.current_energy = 0
		self.initial_energy = 0
		self.energy_parameter = 500*10**(-9) #nJ/bit
		self.free_space_energy_parameter = 25*10**(-12)	#pJ/bit/m^2
		self.multihop_energy_paramter = 0.065*10**(-12)	#pJ/bit/m^2
		self.d0 = math.sqrt(self.free_space_energy_parameter/self.multihop_energy_paramter)


	def	dist_from_node(self, Node)	-> float:
		"""
		distance of node from reference node

		parameters:
		-	Reference Node
		"""
		x1 = self.x
		y1 = self.y
		x2 = Node.x
		y2 = Node.y
		return round(math.sqrt((x1-x2)**2 + (y1-y2)**2), 2)

	def dist_from_server(self, sink):
		"""
		distance of node from sink

		parameters:
		-	[sink x coordinate, sink y coordinate]
		"""
		self.dts = round(math.sqrt((self.x - sink[0])**2 + (self.y - sink[1])**2), 2)
		return self.dts

	def node_energy_setup(self, initial_energy, critical_energy):
		"""
		sets up energy of node

		parameters:
		-	initial energy
		-	critical energy
		"""
		self.initial_energy = initial_energy
		self.current_energy = initial_energy
		self.critical_energy = critical_energy
		return

	def energy_for_transmission(self, k, d):
		"""
		returns energy required for transmission

		parameters:
		-	k: packet length
		-	d: distance of transmission
		"""
		if(d < self.d0):
			return k*(self.energy_parameter + self.free_space_energy_parameter*d**2)
		else:
			return k*(self.energy_parameter + self.multihop_energy_paramter*d**4)

	def energy_for_reception(self, k):
		"""
		returns energy required for reception

		parameters:
		-	k: packet length
		"""
		return k*self.energy_parameter

	def setup_for_leach(self):
		"""
		void function that setup's LEACH protocole
		"""
		self.role = 0 #	not a head
		self.times_elected = 0
		self.last_head_rnd = -1
		self.clusterID = 0
		self.dist_to_head = 1e12
		self.children_clusters = list()

