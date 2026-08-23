from .teg_node import TEGNode as TNode


class TEGEdge:
    def __init__(self, from_node: TNode, to_node: TNode, max_cap: int):
        self.from_node = from_node
        self.to_node = to_node
        self.capacity = max_cap
        self.current_flow = 0
        self.reverse_edge: TEGEdge | None = None

    def get_remaining_flow(self) -> int:
        return self.capacity - self.current_flow

    def augment_edge(self, flow_val: int) -> None:
        self.current_flow += flow_val
        if self.reverse_edge:
            self.reverse_edge.current_flow -= flow_val
