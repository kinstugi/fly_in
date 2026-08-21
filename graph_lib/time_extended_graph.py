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
        nodes: list[TNode] = []
        edges: list[TEdge] = []

        for t in range(self.turns + 1):
            edges.append(TEdge(
                TNode(s_graph.sink_node, t, Role.r_out),
                self.super_sink,
                sys.maxsize)
            )
            for s_node in s_graph.graph.keys():
                u_in_t = TNode(s_node, t, Role.r_in)
                u_out_t = TNode(s_node, t, Role.r_out)

                nodes.extend([u_in_t, u_out_t])
                if s_node in [s_graph.sink_node, s_graph.source_node]:
                    edges.append(TEdge(u_in_t, u_out_t, sys.maxsize))
                else:
                    edges.append(
                        TEdge(u_in_t, u_out_t, u_in_t.node.max_drones)
                    )

        for s_node in s_graph.graph.keys():
            if s_node == s_graph.sink_node:
                pass
            else:
                for edge in s_graph.graph[s_node]:
                    for t in range(self.turns):
                        from_node = TNode(edge.from_node, t, Role.r_out)
                        to_node = TNode(edge.to_node, t+1, Role.r_in)
                        edges.append(TEdge(from_node, to_node, edge.max_link_cap))

            for t in range(self.turns):
                from_node = TNode(s_node, t, Role.r_out)
                to_node = TNode(s_node, t+1, Role.r_in)
                if s_node == s_graph.source_node:
                    edges.append(TEdge(from_node, to_node, sys.maxsize))
                elif s_node == s_graph.sink_node:
                    pass
                else:
                    edges.append(TEdge(from_node, to_node, s_node.max_drones))
