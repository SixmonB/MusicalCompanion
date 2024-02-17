import random
import Graph
import time
import mido
import sys
import json
from Ant import AntMusician, AntUser, AntComposer

def selectOutputPorts():
	ports_output = mido.get_output_names()
	def open_output(idx):
		name = ports_output[int(idx.strip())]
		port = mido.open_output(name)
		print("opened:" + str(port))
		return port
	
	print('Available output ports:')
	for (i, port) in enumerate(ports_output):
		print(str(i), port)
	print("Selection (comma-separated):")
	return list(map(lambda x:open_output(x), next(sys.stdin).split(",")))

def selectInputPort():
	ports_input = mido.get_input_names()
	print('Available input ports: ', ports_input)
	for (i, port) in enumerate(ports_input):
		print(str(i), port)
	print("Selection:")
	idx = int(next(sys.stdin).strip())
	name = ports_input[idx]
	port = mido.open_input(name)
	return port

"""
Holds all the graphs and calls their callback methods (update, on_midi_receive).
"""
class Scheduler:
	def __init__(self, path):
		evaporation_rate = 8
		self.graphs = []
		self.prevUpdate = time.time()
		
		self.output_ports = selectOutputPorts()
		self.input_port = selectInputPort()

		with open(path, "r") as file:
			params = json.load(file)
			self.bpm = float(params["bpm"])
			evaporation_rate = float(params["decay_factor"])
			if "main_graph" in params.keys():
				self.main_graph = int(params["main_graph"])
			for graph_desc in params["graphs"]:
				path = graph_desc["path"]
				graph = Graph.Graph(self, evaporation_rate, source = path)
				for i in range(graph_desc.get("nb_composers", 0)):
					graph.ants.append(AntComposer(graph))
				
				for ant in graph_desc.get("musicians", []):
					graph.ants.append(AntMusician(graph, port=ant["port"], channel=ant["channel"]))

				if "user" in graph_desc.keys():
					ant = graph_desc["user"]
					graph.ants.append(AntUser(graph, port=ant["port"], channel=ant["channel"]))
						
				self.graphs.append(graph)

		self.input_port.callback = self.on_midi_receive

	def on_midi_receive(self, msg):
		if msg.type == "note_on" or msg.type == "note_off":
			for graph in self.graphs:
				graph.on_midi_receive(msg)

	def run(self):
		"""
		The scheduler keeps record of the run routine updates so as to be able to play multiple graphs at the same time.
		It calculates the difference between the present time and the time of the last update and then sends this paramenter to the graph to check
		if there are notes still playing or if it can move on to the next.
		"""
		now = time.time()
		dt = (now - self.prevUpdate)
		self.prevUpdate = now
		for graph in self.graphs:
			graph.run(dt)
			graph.evaporate(dt)


if __name__ == "__main__":
	path = sys.argv[1]
	print("loading from path:", path)
	scheduler = Scheduler(path)
	while True:
		time.sleep(0.001)
		scheduler.run()
