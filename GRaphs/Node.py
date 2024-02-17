class Node:
    def __init__(self, id: int, note: int, velocity: int, duration: float, time: float = 0):
        self.id = id
        self.type = type
        self.note = note
        self.velocity = velocity
        self.duration = duration
        self.time = time
    
    def __repr__(self):
        return f"({self.id}" + ": " + f"({self.type},{self.note}, {self.velocity}, {self.duration})"
