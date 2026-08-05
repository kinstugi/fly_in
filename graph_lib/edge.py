from graph_lib import Node


class Edge:
    def __init__(self, from_node: Node, to_node: Node, max_cap: int = 1):
        self.from_node = from_node
        self.to_node = to_node
        self.max_cap = max_cap
        self.cap = 0
        self.rev: Edge | None = None
    
    def get_remaining_cap(self) -> int:
        return self.max_cap - self.cap
    
    def augment_path(self, val: int) -> None:
        self.cap += val
        if self.rev:
            self.rev.cap -= val
