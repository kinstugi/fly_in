from graph_lib import Edge, Node
from collections import defaultdict


class FlowGraph:
    def __init__(self, source: Node, sink: Node):
        self.graph: defaultdict[Node, list[Edge]] = defaultdict(list)
        self.source_node: Node = source
        self.sink_node: Node = sink

    def add(self, from_node: Node, to_node: Node, cap: int = 1) -> None:
        forward_edge = Edge(from_node, to_node, cap)
        backward_edge = Edge(to_node, from_node, 0)

        forward_edge.rev = backward_edge
        backward_edge.rev = forward_edge

        self.graph[from_node].append(forward_edge)
        self.graph[to_node].append(backward_edge)
