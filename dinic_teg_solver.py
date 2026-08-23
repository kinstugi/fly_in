from graph_lib import TEG, TNode
from collections import deque


class DincTEGSolver:
    def __init__(self, graph: TEG):
        self.teg = graph

    def build_level_graph(self) -> dict[TNode, int]:
        level_graph: dict[TNode, int] = {}
        q: deque[TNode] = deque([self.teg.source_node])
        level_graph[self.teg.source_node] = 0

        while q:
            cnt = len(q)
            done = False

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
                
        return level_graph

    def push_flow(self) -> int:
        return 0

    def get_max_flow(self) -> int:
        return 0
