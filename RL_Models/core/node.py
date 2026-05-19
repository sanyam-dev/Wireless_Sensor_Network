import math

class node:
	"""
	initialises the node

	parameters:
	-	x coordinate of node
	-	y coordinate of node
	-	node id
	"""
	energy_parameter = 500*10**(-9)              #nJ/bit
	free_space_energy_parameter = 25*10**(-12)   #pJ/bit/m^2
	multihop_energy_parameter = 0.065*10**(-12)  #pJ/bit/m^4
	d0 = math.sqrt(free_space_energy_parameter/multihop_energy_parameter)

	def	__init__(self, x, y, id) -> None:
		self.x = x
		self.y = y
		self.id = id
		self.critical_energy = 0
		self.current_energy = 0
		self.initial_energy = 0
		self.packets_this_rnd = 0

	def	dist(self, Node)-> float:
		"""
		distance of node from reference node

		parameters:
		-	Reference Node
		"""
		return round(math.hypot(self.x - Node.x, self.y - Node.y), 2)

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

	def is_functional(self)	-> bool:
		return self.current_energy > self.critical_energy or self.id == 0

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
			return k*(self.energy_parameter + self.multihop_energy_parameter*d**4)

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
		self.clusterID = 0
		self.dist_to_head = 1e12

	def set_packets(self, number_of_packets):
		self.packets_this_rnd = number_of_packets
		return number_of_packets
