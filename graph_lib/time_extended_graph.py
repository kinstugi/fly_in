from graph_lib import StaticGraph, TNode, TEdge, Role
from collections import defaultdict
import sys


class TimeExtendedGraph:
    def __init__(self, turns: int, s_graph: StaticGraph):
        self.turns = turns
        self.graph: dict[TNode, list[TEdge]] = defaultdict(list)
        self.super_source: list[TNode] = []
        self.super_sink: list[TNode] = []
        self.build_graph(s_graph)

    def build_graph(self, s_graph: StaticGraph):
        nodes: list[TNode] = []
        edges: list[TEdge] = []

        for t in range(self.turns + 1):
            for s_node in s_graph.graph.keys():
                u_in_t = TNode(s_node, t, Role.r_in)
                u_out_t = TNode(s_node, t, Role.r_out)

                nodes.extend([u_in_t, u_out_t])
                if s_node == s_graph.sink_node:
                    edges.append(TEdge(u_in_t, u_out_t, sys.maxsize))
                else:
                    edges.append(TEdge(u_in_t, u_out_t, u_in_t.node.max_drones))
