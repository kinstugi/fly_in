from graph_lib import StaticGraph, TNode, TEdge, Role, Node
from collections import defaultdict
import sys


class TimeExtendedGraph:
    def __init__(self, turns: int, s_graph: StaticGraph):
        self.turns = turns
        self.graph: dict[TNode, list[TEdge]] = defaultdict(list)
        # self.super_source = TNode(s_graph.source_node, 0, )
        self.super_sink = TNode(
            Node('SUPER_SINK', x=-1, y=-1, max_drones=sys.maxsize),
            -1, Role.r_in
        )
        self.build_graph(s_graph)

    def build_graph(self, s_graph: StaticGraph):

        for t in range(self.turns + 1):
            sink_node = TNode(s_graph.sink_node, t, Role.r_out)
            self.add_edge(sink_node, self.super_sink, sys.maxsize)

            for s_node in s_graph.graph.keys():
                u_in_t = TNode(s_node, t, Role.r_in)
                u_out_t = TNode(s_node, t, Role.r_out)

                if s_node in [s_graph.sink_node, s_graph.source_node]:
                    self.add_edge(u_in_t, u_out_t, sys.maxsize)
                else:
                    self.add_edge(u_in_t, u_out_t, u_in_t.node.max_drones)

        for s_node in s_graph.graph.keys():
            if s_node == s_graph.sink_node:
                pass
            else:
                for edge in s_graph.graph[s_node]:
                    for t in range(self.turns):
                        from_node = TNode(edge.from_node, t, Role.r_out)
                        to_node = TNode(edge.to_node, t+1, Role.r_in)
                        self.add_edge(from_node, to_node, edge.max_link_cap)

            for t in range(self.turns):
                from_node = TNode(s_node, t, Role.r_out)
                to_node = TNode(s_node, t+1, Role.r_in)
                if s_node == s_graph.source_node:
                    self.add_edge(from_node, to_node, sys.maxsize)
                elif s_node == s_graph.sink_node:
                    pass
                else:
                    self.add_edge(from_node, to_node, s_node.max_drones)

    def add_edge(self, from_node: TNode, to_node: TNode, link_cap: int) -> None:
        forward_edge = TEdge(from_node, to_node, link_cap)
        reverse_edge = TEdge(to_node, from_node, 0)

        forward_edge.reverse_edge  = reverse_edge
        reverse_edge.reverse_edge = forward_edge

        self.graph[from_node].append(forward_edge)
        self.graph[to_node].append(reverse_edge)
