from graph_lib import Edge, FlowGraph, Node
from collections import deque, defaultdict


class DinicsMaxFlow:
    def __init__(self, graph: FlowGraph):
        self.graph = graph

    def build_level_graph(self) -> tuple[bool, dict[int, set[Node]] | None]:
        q = deque([self.graph.source_node])
        lvl_graph = defaultdict(set)
        seen: set[Node] = set([self.graph.source_node])
        level = 0
        lvl_graph[level].add(self.graph.source_node)

        while q:
            cnt = len(q)
            for _ in range(cnt):
                nd = q.popleft()
                if nd == self.graph.sink_node:
                    return True, lvl_graph
                
                for edge in self.graph.graph[nd]:
                    if edge.to_node in seen or edge.get_remaining_cap() < 1:
                        continue
                    seen.add(edge.to_node)
                    q.append(edge.to_node)
                    lvl_graph[level+1].add(edge.to_node)
            level += 1
        return False, None
    
    def find_augment_path(self, lvl_graph: dict[int, set[Edge]]) -> bool:
        stk = [(self.graph.source_node, 0)]
        bottle_neck = float('inf')
        found = False
        path_taken = []

        while stk:
            nd, lvl = stk.pop()
            if nd == self.graph.sink_node:
                found = True
                break
            for edge in self.graph.graph[nd]:
                if edge.to_node not in lvl_graph[lvl+1] or edge.get_remaining_cap() < 1:
                    continue
                stk.append((edge.to_node, lvl+1))
                bottle_neck = min(bottle_neck, edge.get_remaining_cap())

    def solve(self):
        while True:
            has_lvl_graph, lvl_graph = self.build_level_graph()
            if not has_lvl_graph:
                break
            did_augment = self.find_augment_path(lvl_graph)
            if not did_augment:
                break
