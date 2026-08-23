from collections import defaultdict
from graph_lib import Node, Edge


class StaticGraph:
    def __init__(self, start_node: Node, end_node: Node):
        self.graph: dict[Node, list[Edge]] = defaultdict(list)
        self.source_node = start_node
        self.sink_node = end_node

    def add_connection(self, a: Node, b: Node, cap: int) -> None:
        self.graph[a].append(Edge(a, b, cap))
        self.graph[b].append(Edge(b, a, cap))
