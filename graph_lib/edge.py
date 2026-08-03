from graph_lib import Node


class Edge:
    def __init__(self, node_a: Node, node_b: Node, max_cap: int = 1):
        self.from_node = node_a
        self.to_node = node_b
        self.max_cap = max_cap
        self.cap = 0
        self.rev: Edge | None = None
    
    def get_remaining_cap(self) -> int:
        return self.max_cap - self.cap
    
    def augment_path(self, val: int) -> None:
        self.cap += val
        if self.rev:
            self.rev.cap -= val
