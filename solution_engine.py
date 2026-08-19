from graph_lib import StaticGraph, TEG
from dinic_teg_solver import DincTEGSolver


class SolutionEngine:
    def __init__(self, graph: StaticGraph, num_drones: int):
        self.graph = graph
        self.num_drones = num_drones

    def find_optimal_time(self) -> int:
        low, high = 1, 80
        ans = 0

        while low <= high:
            mid = (low + high) // 2
            teg = TEG(mid, self.graph)
            dinic = DincTEGSolver(teg)
            max_flow = dinic.get_max_flow()

            if max_flow >= self.num_drones:
                ans = mid
                high = mid - 1
            elif max_flow < mid:
                low  = mid + 1
        return ans
