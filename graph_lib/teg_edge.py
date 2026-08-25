from .teg_node import TEGNode as TNode


class SharedCapacity:
    """Capacity shared by multiple forward TEG edges."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.used = 0


class TEGEdge:
    def __init__(
        self,
        from_node: TNode,
        to_node: TNode,
        max_cap: int,
        shared_capacity: SharedCapacity | None = None,
        shared_direction: int = 1,
    ):
        self.from_node = from_node
        self.to_node = to_node
        self.capacity = max_cap
        self.current_flow = 0
        self.reverse_edge: TEGEdge | None = None
        self.shared_capacity = shared_capacity
        self.shared_direction = shared_direction

    def get_remaining_flow(self) -> int:
        if self.shared_capacity and self.shared_direction == 1:
            return self.shared_capacity.capacity - self.shared_capacity.used
        return self.capacity - self.current_flow

    def augment_edge(self, flow_val: int) -> None:
        if self.shared_capacity:
            self.shared_capacity.used += self.shared_direction * flow_val
        self.current_flow += flow_val
        if self.reverse_edge:
            self.reverse_edge.current_flow -= flow_val
