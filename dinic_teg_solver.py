from graph_lib import TEG, Node
from collections import deque


class DincTEGSolver:
    def __init__(self, graph: TEG):
        self.teg = graph

    def build_level_graph(self) -> dict[Node, int]:
        return {}

    def push_flow(self) -> int:
        return 0

    def get_max_flow(self) -> int:
        return 0
