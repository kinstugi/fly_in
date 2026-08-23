from graph_lib import TEG, TNode, TEdge
from collections import deque
import sys


class DincTEGSolver:
    def __init__(self, graph: TEG):
        self.teg = graph

    def build_level_graph(self) -> dict[TNode, int]:
        level_graph: dict[TNode, int] = {}
        q: deque[TNode] = deque([self.teg.source_node])
        level_graph[self.teg.source_node] = 0
        done = False

        while q:
            cnt = len(q)

            for _ in range(cnt):
                nd = q.popleft()
                if nd == self.teg.sink_node:
                    done = True
                for edge in self.teg.graph[nd]:
                    if level_graph.get(edge.to_node, -1) != -1 or edge.get_remaining_flow() < 1:
                        continue
                    q.append(edge.to_node)
                    level_graph[edge.to_node] = level_graph[nd] + 1
            if done:
                break
        if not done:
            return {}
        return level_graph

    def push_flow(self, level_graph: dict[TNode, int], ptr: dict[TNode, int]) -> int:
        def helper_checker(edge: TEdge, nd: TNode) -> bool:
            a = level_graph.get(edge.to_node, -1)
            return (
                edge.get_remaining_flow() > 0 and
                a == level_graph.get(nd, -1) + 1
            )

        def recur(nd: TNode, in_flow: int) -> int:
            if nd == self.teg.sink_node or in_flow < 1:
                return in_flow
            edges = self.teg.graph[nd]
            while ptr[nd] < len(edges):
                edge = edges[ptr[nd]]
                if helper_checker(edge,  nd):
                    bottle_neck = min(in_flow, edge.get_remaining_flow())
                    pushed = recur(edge.to_node, bottle_neck)
                    if pushed > 0:
                        edge.augment_edge(pushed)
                        return pushed
                ptr[nd] += 1
            return 0
        return recur(self.teg.source_node, sys.maxsize)

    def get_max_flow(self) -> int:
        max_flow = 0
        while True:
            level_graph = self.build_level_graph()
            if not level_graph:
                break
            ptr = {nd: 0 for nd in self.teg.graph}
            while True:
                pushed = self.push_flow(level_graph, ptr)
                if pushed < 1:
                    break
                max_flow += pushed
        return max_flow
