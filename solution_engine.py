from graph_lib import StaticGraph, TEG
from dinic_teg_solver import DincTEGSolver


class SolutionEngine:
    def __init__(self, graph: StaticGraph, num_drones: int):
        self.graph = graph
        self.num_drones = num_drones

    def find_optimal_time(self) -> tuple[int, TEG | None]:
        low, high = 1, 80
        optimal_time = 0
        optimal_teg: TEG | None = None

        while low <= high:
            mid = (low + high) // 2
            teg = TEG(mid, self.graph)
            dinic = DincTEGSolver(teg)
            max_flow = dinic.get_max_flow()

            if max_flow >= self.num_drones:
                optimal_time = mid
                optimal_teg = teg
                high = mid - 1
            elif max_flow < self.num_drones:
                low  = mid + 1
        return optimal_time, optimal_teg
