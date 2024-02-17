import os
import json
import random
import mido
import time
import scipy.special
import math
from Node import Node

class Graph : 
    """
    Holds nodes & edges of a graph, and the ants inside it.
    Calls update & on_midi_receive for the ants.
    Computes probabilities corresponding to each edge
    """

    def __init__(self, scheduler, evaporation_rate: float, nodes={}, edges={}, source = None, name = "", length=4):
        self.scheduler = scheduler
        self.loop_position = 0
        self.loop_length = length
        self.nodes = nodes
        self.edges = edges
        self.root_node = 1
        self.evaporation_rate = evaporation_rate
        self.ants = []
        self.name = name
        if source:
            self.load(source)

    def on_midi_receive(self, msg):
        for ant in self.ants:
            ant.on_midi_receive(msg, self.loop_position)

    def load(self, path):
        """
        Loads a music graph from a json file
        Returns a list with Node and Edge objects
        """
        with open(path) as f:
            self.data = json.load(f)

        if not self.name:
            self.name = self.data["name"]
        
        if "loop_duration" in self.data.keys():
            self.loop_length = self.data["loop_duration"]

        self.nodes = {}
        for attributes in self.data['nodes']:
            attributes.setdefault("position", 0)
            node = Node(attributes["id"], attributes["note"], attributes["velocity"], attributes["duration"], attributes["position"])
            node.id = int(node.id[1:])
            self.nodes[node.id] = node
        

        self.edges = {}
        self.last_edge_id = 0
        for attributes in self.data['edges']:
            edge = Edge(attributes["id"],attributes["originID"], attributes["destinationID"], attributes["weight"])
            edge.id = int(edge.id[1:])
            self.edges[edge.id] = edge
            if(edge.id > self.last_edge_id):
                self.last_edge_id = edge.id

        self.source = os.path.splitext(path)[0] # without extension

    def write(self, previous_node, new_node_id, new_note, position):
        self.last_edge_id += 1
        new_node = {"id": "n"+str(new_node_id),
                    "type": "note",
                    "note": new_note,
                    "velocity": 70,
                    "position": position,
                    "duration": 0.5
                    }
        new_edge = {
                    "id": "e"+str(self.last_edge_id),
                    "originID": previous_node,
                    "destinationID": new_node_id,
                    "weight": 1
                    }
        with open(self.source+"-modified.json", 'w') as f:
            self.data["edges"].append(new_edge)
            self.data["nodes"].append(new_node)
            json.dump(self.data, f, indent = 4)


    def link_or_insert_node_from(self, prev_node_id, node):
        existing_node = [n for n in self.nodes if self.nodes[n].note == node.note and self.nodes[n].time == node.time]
        node_id = None
        if len(existing_node) > 0:
            node_id = self.nodes[existing_node[0]].id
        else:
            self.nodes[node.id] = node
            node_id = node.id

        existing_edge = [e for e in self.edges if self.edges[e].origin == prev_node_id and self.edges[e].destination == node_id]
        edge_id = None
        if len(existing_edge) > 0:
            edge_id = self.edges[existing_edge[0]].id
        else:
            edge = Edge(random.randint(1, 1000000000), prev_node_id, node_id, 1)
            self.edges[edge.id] = edge
            edge_id = edge.id
        return node_id, edge_id

    def create_or_reinforce_node(self, prev_node_id, note, loop_position):
        # node = (n for n in self.nodes if n.note == note and loop_position == )
        pass

    def get_first_element_graph(self):
        # we keep only the number of the id by removing the identifier 'n'
        """
        Reads the first note of the graph to start playing
        """
        first_graph_element = self.nodes[0].id[1:]
        return int(first_graph_element)

    def get_linked_edges(self, node_id):
        linked_edges = []
        for _, edge in self.edges.items():
            # we keep only the number of the id of the edges coming from the current note
            if edge.origin == node_id:
                linked_edges.append(edge)
        return linked_edges

    def random_selection(self, linked_nodes):
        """
        If there are more than 1 possible edge, it chooses one randomly according to the probability distribution
        """
        if len(linked_nodes) >= 1:
            weights = [linked_node.weight for linked_node in linked_nodes]
            selected_edge = random.choices(linked_nodes, weights)
            return selected_edge[0]
        else:
            return None
    
    
    def create_ants(self, current_note, amount_of_composers, amount_of_musicians):
        """
        Creates a list of composer ants and 1 musician or a list of musicians depending on argument of the function
        """
        for i in range(amount_of_composers):
            self.composers.append(Ant(current_note, "composer"))
        
        if(amount_of_musicians == 1):
            self.musician = Ant(current_note, "musician")
        else:
            self.musician = []
            for i in range(amount_of_musicians):
                self.musicians.append(Ant(current_note, "musician"))

    def evaporate(self, dt):
        for _, edge in self.edges.items():
            interp_t = 1 - math.exp(-self.evaporation_rate * dt)
            edge.pheromone = edge.pheromone * (1 - interp_t)
        

    def calculate_probabilities(self, ant):
        """
        Uses a softmax normalisation to recalculate the edges' probabilities according to the amount of pheromones placed
        """
        if len(ant.linked_edges_to_current_node) > 1:
            linked_edges_pheromones = [linked_edge.pheromone for linked_edge in ant.linked_edges_to_current_node]
            # print(linked_edges_pheromones)
            t = 6
            x_t = [xi/t for xi in linked_edges_pheromones]
            softmax_list = scipy.special.softmax(x_t)
            # print(softmax_list)
            for i, linked_edges in enumerate(ant.linked_edges_to_current_node):
                linked_edges.weight = softmax_list[i]

    def run(self, dt):
        self.loop_position += dt*(self.scheduler.bpm/60)
        if self.loop_position >= self.loop_length:
            self.loop_position = self.loop_position%self.loop_length
            for ant in self.ants:
                ant.reset()
        
        for ant in self.ants:
            ant.run(dt*(self.scheduler.bpm/60))

class Edge : 
    def __init__(self, id, origin, destination, weight):
        self.id = id
        self.origin = origin
        self.destination = destination
        self.weight = weight
        self.pheromone = 0

    def __repr__(self):
        return f"({self.id} : from {self.origin} to {self.destination} with odds :  {self.weight})"

if __name__ == "__main__":
    decay = 8
    amount_of_composers = 100
    amount_of_musicians = 1

    graph = Graph(decay)
    graph.load()

    # current note type: Node
    current_note = graph.nodes[0]

    # list of composer ants and musicians
    graph.create_ants(current_note, amount_of_composers, amount_of_musicians)

        
        
