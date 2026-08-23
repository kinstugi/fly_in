from graph_lib import TEG, TEdge, TNode


class TEGDecomposer:
    def __init__(self, graph: TEG, num_drones: int):
        self.teg = graph
        self.num_drones = num_drones
        self.drone_paths: list[list[TEdge]] = []

    def decompose(self) -> list[list[TEdge]]:
        drone_path: list[TEdge] = []

        def recur(nd: TNode) -> bool:
            if nd == self.teg.sink_node:
                self.drone_paths.append(drone_path[:])
                drone_path.clear()
                return True

            edges = self.teg.graph[nd]
            for edge in edges:
                if edge.current_flow < 1:
                    continue
                drone_path.append(edge)
                if recur(edge.to_node):
                    edge.augment_edge(-1)
                    return True
                drone_path.pop()
            return False

        i = 0
        while recur(self.teg.source_node):
            i += 1
            if i >= self.num_drones:
                break
        return self.drone_paths
