from PyQt6 import QtGui, QtSvgWidgets, QtWidgets, QtCore
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget

from Ant import AntMusician, AntUser
import Graph
from Scheduler import Scheduler
import pydot
import time
import math
import sys

def format_note(nb):
	note = nb % 12
	return [
		"Do",
		"Do#",
		"Ré",
		"Ré#",
		"Mi",
		"Fa",
		"Fa#",
		"Sol",
		"Sol#",
		"La",
		"La#",
		"Si",
	][note]

def render_graph(scheduler):
	time_start = time.time()
	dotgraph = pydot.Dot("main_graph", graph_type="digraph")
	for (i, graph) in enumerate(scheduler.graphs):
		subgraph = pydot.Subgraph(graph_name="subgraph-{}".format(i))
		subgraph.set("label", "aaa")
		nodes = {}
		node_ids = list(graph.nodes.keys())
		timed_subgraphs = {}
		for node_id in node_ids:
			node = graph.nodes[node_id]
			if not (str(node.time) in timed_subgraphs.keys()):
				sgname = "t-{}-{}".format(i, node.time)
				timed_subgraphs[str(node.time)] = pydot.Subgraph(graph_name=sgname, label=sgname, rank="same", color="blue")
			color = "white"
			fillcolor = "white"
			for ant in graph.ants:
				if ant.node_id == node_id:
					color = ant.color
				if type(ant) is AntUser:
					fillcolor = "darkolivegreen1"

			# if node == graph.user_node:
			# 	color = "green"

			name = "{}-{}".format(graph.name, node_id)
			nodes[node.id] = pydot.Node(name, label=format_note(graph.nodes[node_id].note), color=color, fillcolor=fillcolor, style="filled")
			timed_subgraphs[str(node.time)].add_node(nodes[node.id])
			# subgraph.add_node(nodes[node.id])
		
		edge_ids = list(graph.edges.keys())
		for edge_id in edge_ids:
			edge = graph.edges[edge_id]
			color = str((0.666-math.tanh(edge.pheromone*0.2)*0.666)%1) + ", 1, 1"
			origin = "{}-{}".format(graph.name, edge.origin)
			destination = "{}-{}".format(graph.name, edge.destination)
			# prob = edge.weight
			# print(edge)
			e = pydot.Edge(origin, destination, penwidth=5, color=color, label="{:10.2f}".format(edge.weight))
			subgraph.add_edge(e)

		for sg in timed_subgraphs:
			subgraph.add_subgraph(timed_subgraphs[sg])

		dotgraph.add_subgraph(subgraph)
	
	svg = dotgraph.create_svg()
	# print("creating svg took {:.3f} seconds".format(time.time()-time_start))
	return svg

class MainWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.upd)
		self.timer.start(1)

		self.render_timer = QtCore.QTimer()
		self.render_timer.timeout.connect(self.render_upd)
		self.render_timer.start(100)

		self.svg_widget = QtSvgWidgets.QSvgWidget("output.svg")
		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(self.svg_widget)

		self.scheduler = Scheduler(sys.argv[1])
		self.svg_widget.load(render_graph(self.scheduler))
		self.render_threads = []
		self.render_workers = []

	def upd(self):
		self.scheduler.run()
	
	def render_upd(self):
		thread = QThread()
		worker = Worker(self.scheduler)
		worker.moveToThread(thread)
		thread.started.connect(worker.run)
		worker.finished.connect(thread.quit)
		worker.finished.connect(worker.deleteLater)
		thread.finished.connect(thread.deleteLater)
		worker.finished.connect(self.render_receive)
		thread.start()
		self.render_threads.append(thread)
		self.render_workers.append(worker)

	def render_receive(self, svg):
		self.svg_widget.load(svg)

class Worker(QObject):
	finished = pyqtSignal(bytes)

	def __init__(self, scheduler):
		super().__init__()
		self.scheduler = scheduler

	def run(self):
		svg = render_graph(self.scheduler)
		self.finished.emit(svg)

app = QtWidgets.QApplication([])
win = MainWindow()
win.show()
app.exec()
