from graph_lib import TEdge, Role


class OutputFormatter:
    """Convert decomposed TEG paths into Fly-in turn output."""

    _ANSI_COLORS = {
        "black": "30",
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "white": "37",
        "gray": "90",
        "grey": "90"
    }

    def format(
        self,
        paths: list[list[TEdge]],
        turns: int,
        visual: bool = False
    ) -> str:
        """Return one movement line for each simulation turn."""
        movements: dict[int, list[str]] = {}

        for drone_id, path in enumerate(paths, start=1):
            for edge in path:
                movement = self._movement(drone_id, edge)
                if movement is None:
                    continue
                turn, token = movement
                if visual:
                    token = self._color_token(token, edge)
                movements.setdefault(turn, []).append(token)

        lines = []
        for turn in range(1, turns + 1):
            turn_movements = " ".join(movements.get(turn, []))
            if visual:
                if not turn_movements:
                    turn_movements = "waiting"
                lines.append(f"Turn {turn}: {turn_movements}")
            else:
                lines.append(turn_movements)
        return "\n".join(lines)

    def _color_token(self, token: str, edge: TEdge) -> str:
        destination = edge.to_node.node
        color = (
            "red"
            if destination.name.startswith("__TRANSIT__")
            else destination.color
        )
        if color is None:
            return token
        ansi_code = self._ANSI_COLORS.get(color.lower())
        if ansi_code is None:
            return token
        return f"\033[{ansi_code}m{token}\033[0m"

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
