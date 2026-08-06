from graph_lib import Edge, FlowGraph, Node
from collections import deque, defaultdict


class DinicsMaxFlow:
    def __init__(self, graph: FlowGraph):
        self.graph = graph

    def build_level_graph(self) -> tuple[bool, dict[Node, int] | None]:
        q = deque([self.graph.source_node])
        lvl_graph: dict[Node, int]  = dict()
        lvl_graph[self.graph.source_node] = 0
        terminate = False

        while q and not terminate:
            cnt = len(q)
            for _ in range(cnt):
                nd = q.popleft()
                if nd == self.graph.sink_node:
                    terminate = True
                for edge in self.graph.graph[nd]:
                    if edge.get_remaining_cap() < 1 or lvl_graph.get(edge.to_node, -1) != -1:
                        continue
                    lvl_graph[edge.to_node] = lvl_graph[nd] + 1
                    q.append(edge.to_node)
        if terminate:
            return True, lvl_graph
        return False, None

    def find_augment_path(self, lvl_graph: dict[Node, int], ptr: dict[Node, int]) -> int:
        def recur(nd: Node, in_flow: int) -> int:
            if nd == self.graph.sink_node or in_flow < 1:
                return in_flow

            edges = self.graph.graph[nd]
            while ptr[nd] < len(edges):
                edge = edges[ptr[nd]]
                if edge.get_remaining_cap() > 0 and lvl_graph.get(nd, -1) + 1 == lvl_graph.get(edge.to_node):
                    bottleneck = min(in_flow, edge.get_remaining_cap())
                    pushed = recur(edge.to_node, bottleneck)
                    if pushed > 0:
                        edge.augment_path(pushed)
                        return pushed
                ptr[nd] += 1
            return 0
        return recur(self.graph.source_node, float('inf'))

    def solve(self) -> int:
        max_flow = 0
        while True:
            has_lvl_graph, lvl_graph = self.build_level_graph()
            if not has_lvl_graph:
                break

            ptr = {nd: 0 for nd in self.graph.graph}
            while True:
                pushed = self.find_augment_path(lvl_graph, ptr)
                if pushed < 1:
                    break
                max_flow += pushed
        return max_flow

    def path_decomposition(self) -> list[list[Edge]]:
        paths: list[list[Edge]] = []
        path: list[Edge] = []

        def recur(nd: Node) -> bool:
            if nd == self.graph.sink_node:
                paths.append(path[:])
                return True
            
            for edge in self.graph.graph[nd]:
                if edge.cap < 1:
                    continue
                path.append(edge)
                if recur(edge.to_node):
                    edge.cap -= 1
                    return True
                path.pop()
            return False
        
        while recur(self.graph.source_node):
            pass
        return paths
