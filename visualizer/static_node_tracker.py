from graph_lib import Role, StaticGraph, TEdge


class StaticGraphStateTracker:
    """Track zone and directed-link occupancy for every simulation turn.

    ``state_per_turn[t]`` contains occupancy counts using these keys:

    * ``zone:<name>`` is the number of drones occupying a physical zone.
    * ``link:<from>-<to>`` is the number of drones using a directed link.

    Restricted movement is represented by its synthetic transit node in the
    TEG.  Its occupancy is reported as the corresponding physical link.
    """

    def __init__(
        self,
        drone_path: list[list[TEdge]],
        s_graph: StaticGraph,
    ):
        self.s_graph = s_graph
        self.state_per_turn = self._build(drone_path)

    def _build(self, drone_path: list[list[TEdge]]) -> list[dict[str, int]]:
        """Build occupancy counts indexed by TEG time."""
        horizon = max(
            (
                max(
                    (edge.to_node.t for edge in path),
                    default=0,
                )
                for path in drone_path
            ),
            default=0,
        )
        state: list[dict[str, int]] = [
            {} for _ in range(horizon + 1)
        ]

        for path in drone_path:
            for edge in path:
                movement = self._parse_edge(edge)
                if movement is None:
                    continue
                turn, key = movement
                state[turn][key] = state[turn].get(key, 0) + 1
        return state

    def _parse_edge(self, edge: TEdge) -> None | tuple[int, str]:
        """Convert one solved TEG edge into an occupancy event."""
        from_node = edge.from_node
        to_node = edge.to_node

        if to_node.node.name == "SUPER_SINK":
            return None

        # A zone split edge means that the drone occupies the node at t.
        if from_node.role == Role.r_in and to_node.role == Role.r_out:
            if from_node.node.name.startswith("__TRANSIT__"):
                return from_node.t, self._transit_key(from_node.node.name)
            return from_node.t, f"zone:{from_node.node.name}"

        # Movement edges represent a directed link during the interval that
        # starts at from_node.t. Waiting edges do not change link occupancy.
        if from_node.role != Role.r_out or to_node.role != Role.r_in:
            return None
        if from_node.node.name == to_node.node.name:
            return None
        if to_node.node.name.startswith("__TRANSIT__"):
            return None
        if from_node.node.name.startswith("__TRANSIT__"):
            return None
        return from_node.t, f"link:{from_node.node.name}-{to_node.node.name}"

    @staticmethod
    def _transit_key(transit_name: str) -> str:
        """Convert a synthetic transit node name to its physical link key."""
        body = transit_name.removeprefix("__TRANSIT__")
        connection = body.rsplit("__", 1)[0]
        parts = connection.rsplit("__", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid transit node: {transit_name}")
        return f"link:{parts[0]}-{parts[1]}"
