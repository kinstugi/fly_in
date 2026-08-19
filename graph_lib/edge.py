from graph_lib import Node


class Edge:
    def __init__(self, from_node: Node, to_node: Node, max_cap: int = 1):
        self.from_node = from_node
        self.to_node = to_node
        self.max_link_cap = max_cap
