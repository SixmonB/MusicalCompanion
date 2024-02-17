import mido
import random
import time
import math
from Node import Node

class Ant:
    def __init__(self, graph, first_node: int = 1):
        self.graph = graph
        self.node_id = first_node
        self.influence = 1
        self.calculate_pheromones = False
        self.linked_edges_to_current_node = []
        self.color = "red"

    def reset(self):
        roots = [n for n in self.graph.nodes if self.graph.nodes[n].time == 0]
        print(len(roots))
        idx = random.randint(0, len(roots)-1)
        self.node_id = roots[idx]

    def current_node(self):
        return self.graph.nodes[self.node_id]

    def on_midi_receive(self, msg, time):
        pass

    def place_pheromone(self, chosen_edge):
        chosen_edge.pheromone += self.pheromone_intensity

    def move(self):
        """
        Traverse an edge, changing the current node and placing pheromones along the way.
        """
        # print("edge: ", edge)
        if self.chosen_edge is not None:
            self.node_id = self.chosen_edge.destination
            self.place_pheromone(self.chosen_edge)
        # graph.distribute_pheromone(self.current_node, 1)
        # pheromones = [node.pheromone for node in graph.nodes]
        # print(pheromones)

    def chooseNextEdge(self):
        self.graph.calculate_probabilities(self)
        self.linked_edges_to_current_node = self.graph.get_linked_edges(self.node_id)
        self.chosen_edge = self.graph.random_selection(self.linked_edges_to_current_node)
        
    def next_node(self):
        if self.chosen_edge is not None:
            return self.graph.nodes[self.chosen_edge.destination]
        else:
            return None

class AntComposer(Ant):
    """
    This ant moves through the graph and plays notes corresponding to each node.
    Arguments:
    - Parent graph
    - MIDI channel
    """
    def __init__(self, graph):
        super().__init__(graph)
        self.delay = 0 # delay until the end of the current note
        self.calculate_pheromones = True
        self.chooseNextEdge()
        self.pheromone_intensity = 0.2
        self.color = "purple"

    def chooseNextEdge(self):
        self.linked_edges_to_current_node = self.graph.get_linked_edges(self.node_id)
        if len(self.linked_edges_to_current_node) > 0:
            idx = random.randint(0, len(self.linked_edges_to_current_node)-1)
            self.chosen_edge = self.linked_edges_to_current_node[idx]
        else:
            self.chosen_edge = None

    def reset(self):
        if len(self.graph.get_linked_edges(self.node_id)) == 0:
            super().reset()
            self.chooseNextEdge()

    def run(self, dt: float):
        time = self.graph.loop_position
        # If we were in a dead end, check if a new node has appeared
        if self.next_node() is None:
            self.chooseNextEdge()

        # To prevent looping multiple times if `dt` is very large, we keep track of the already visited nodes
        visited_nodes = set({})
        while self.next_node() is not None and (not self.next_node().id in visited_nodes):
            # print(self.graph.loop_position, dt, self.next_node().time)

            move = False
            if time-dt >= 0:
                move = time >= self.next_node().time and time-dt < self.next_node().time
            else:
                move = time >= self.next_node().time or (time-dt)%self.graph.loop_length < self.next_node().time

            visited_nodes.add(self.next_node().id)

            if move:
                self.move()
                self.chooseNextEdge()
            else:
                return
            

class AntMusician(Ant):
    """
    This ant moves through the graph and plays notes corresponding to each node.
    Arguments:
    - Parent graph
    - MIDI channel
    """
    def __init__(self, graph, port: int, channel: int):
        super().__init__(graph)
        self.port = port
        self.channel = channel
        self.delay = 0 # delay until the end of the current note
        self.calculate_pheromones = True
        msg = mido.Message('note_on', note = self.current_node().note, velocity=30, channel = self.channel)
        self.graph.scheduler.output_ports[self.port].send(msg)
        self.pheromone_intensity = 0.1
        self.chooseNextEdge()

    def reset(self):
        if len(self.graph.get_linked_edges(self.node_id)) == 0:
            
            msg = mido.Message('note_off', note = self.current_node().note, channel = self.channel)
            self.graph.scheduler.output_ports[self.port].send(msg)
            super().reset()
            msg = mido.Message('note_on', note = self.current_node().note, velocity=100, channel = self.channel)
            self.graph.scheduler.output_ports[self.port].send(msg)
            
            self.chooseNextEdge()

    def run(self, dt: float):
        time = self.graph.loop_position

        # If we were in a dead end, check if a new node has appeared
        if self.next_node() is None:
            self.chooseNextEdge()

        # To prevent looping multiple times if `dt` is very large, we keep track of the already visited nodes
        visited_nodes = set({})
        while self.next_node() is not None and (not self.next_node().id in visited_nodes):
            # print(self.graph.loop_position, dt, self.next_node().time)
            move = False
            if time-dt >= 0:
                move = time >= self.next_node().time and time-dt < self.next_node().time
            else:
                move = time >= self.next_node().time or (time-dt)%self.graph.loop_length < self.next_node().time

            visited_nodes.add(self.next_node().id)

            if move:
                msg = mido.Message('note_off', note = self.current_node().note, channel = self.channel)
                self.graph.scheduler.output_ports[self.port].send(msg)
                self.move()
                msg = mido.Message('note_on', note = self.current_node().note, velocity=100, channel = self.channel)
                self.graph.scheduler.output_ports[self.port].send(msg)
                
                self.chooseNextEdge()
            else:
                return

class AntUser(Ant):
    """
    This ant moves through the graph as the user plays notes.
    If the user plays a note not currently in the graph, it doesn't move
    Arguments:
    - Parent graph
    - MIDI channel
    """
    def __init__(self, graph, port: int, channel: int):
        super().__init__(graph)
        self.port = port
        self.channel = channel
        self.delay = 0 # delay until the end of the current note
        self.calculate_pheromones = False
        self.color = "green"

    def on_midi_receive(self, msg, time):
        # print(self.graph.nodes)
        current_time = self.graph.nodes[self.node_id]
        # elapsed = now - self.last_timestamp
        if msg.type == "note_on":
            new_node_id = random.randint(1, 1000000000)
            # time = time
            time = quantize(time, self.graph.loop_length)
            new_node_id, edge_id = self.graph.link_or_insert_node_from(self.node_id, Node(new_node_id, msg.note, 70, 0.5, time))
            self.graph.write(self.node_id, new_node_id, msg.note, time)
            self.node_id = new_node_id
            self.graph.edges[edge_id].pheromone += 8

        msg.channel = self.channel
        msg.velocity = 120
        self.graph.scheduler.output_ports[self.port].send(msg)

    def reset(self):
        pass

    def run(self, dt):
        pass


# Quantize a loop position according to allowed values
def quantize(time, loop_length):
    time_within_beat = time%1
    beat = math.floor(time)
    ref_points = [0, 0.3333, 0.5, 0.6666, 1]
    # ref_points = [0, 0.5, 1]
    # ref_points = [0, 1]
    closest = math.inf
    closest_pt = 0
    for pt in ref_points:
        dist = abs(time_within_beat-pt)
        if dist < closest:
            closest = dist
            closest_pt = pt
    return (closest_pt+beat)%loop_length

# Testing #

if __name__ == "__main__":
    scheduler = Scheduler(120)
    graph = Graph.Graph(scheduler, source = "freres.json")
    graph.ants.append(AntMusician(graph, 1))
    while True:
        time.sleep(0.001)
        scheduler.run()
