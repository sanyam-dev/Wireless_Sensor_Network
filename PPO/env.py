from network import network as nw

class env:
	def __init__(self) -> None:
		self.net = nw(500, 500, 300, 0, 0)
		self.net.initialise_nodes(1, 0.2)
		self.net.set_parameters(2000,200,2000,2000, 30)
		self.net.show_network()
		