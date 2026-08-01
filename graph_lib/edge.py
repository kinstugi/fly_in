from graph_lib import Node


class Edge:
    def __init__(self, node_a: Node, node_b: Node, max_cap: int = 1):
        self.node_a = node_a
        self.node_b = node_b
        self.edge_cap = max_cap
