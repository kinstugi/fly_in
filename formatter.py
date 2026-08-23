from graph_lib import TEdge, Role


class OutputFormatter:
    """Convert decomposed TEG paths into Fly-in turn output."""

    def format(self, paths: list[list[TEdge]], turns: int) -> str:
        """Return one space-separated movement line for each simulation turn."""
        movements: dict[int, list[str]] = {}

        for drone_id, path in enumerate(paths, start=1):
            for edge in path:
                movement = self._movement(drone_id, edge)
                if movement is None:
                    continue
                turn, token = movement
                movements.setdefault(turn, []).append(token)

        lines = []
        for turn in range(1, turns + 1):
            lines.append(" ".join(movements[turn]))
        return "\n".join(lines)

    def _movement(self, drone_id: int, edge: TEdge) -> tuple[int, str] | None:
        """Translate one TEG transition into an output movement."""
        from_node = edge.from_node
        to_node = edge.to_node

        # Zone-capacity edges, transit-capacity edges, and the super-sink edge
        # are implementation details and do not produce output.
        if from_node.role != Role.r_out or to_node.role != Role.r_in:
            return None
        if to_node.node.name == "SUPER_SINK":
            return None

        # Waiting keeps the drone in the same physical zone and is omitted
        # from the required output format.
        if from_node.node.name == to_node.node.name:
            return None

        if to_node.node.name.startswith("__TRANSIT__"):
            destination = self._transit_destination(to_node.node.name)
            connection = f"{from_node.node.name}-{destination}"
            return to_node.t, f"D{drone_id}-{connection}"

        return to_node.t, f"D{drone_id}-{to_node.node.name}"

    def _transit_destination(self, transit_name: str) -> str:
        """Extract the physical destination from a synthetic transit name."""
        body = transit_name.removeprefix("__TRANSIT__")
        destination_with_time = body.rsplit("__", 1)[0]
        return destination_with_time.rsplit("__", 1)[-1]
