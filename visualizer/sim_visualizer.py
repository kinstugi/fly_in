from dataclasses import dataclass
from typing import Any
import warnings

import pygame

from graph_lib import Node, Role, StaticGraph, TEdge, ZoneType
from .static_node_tracker import StaticGraphStateTracker


@dataclass
class DroneState:
    """A drone's physical state at one TEG time layer."""

    node: Node
    transit_from: Node | None = None
    transit_to: Node | None = None

    @property
    def in_transit(self) -> bool:
        """Return whether the drone is currently crossing a connection."""
        return self.transit_from is not None and self.transit_to is not None


class SimVisualizer:
    """Animate the solved drone schedule over the static map."""

    _WIDTH = 1280
    _HEIGHT = 720
    _MARGIN = 80
    _NODE_RADIUS = 18
    _DRONE_RADIUS = 9
    _TURN_SECONDS = 1.0

    def __init__(
        self,
        s_graph: StaticGraph,
        drone_paths: list[list[TEdge]],
        turns: int,
        show_capacity: bool = True,
    ):
        pygame.init()
        self.screen = pygame.display.set_mode((self._WIDTH, self._HEIGHT))
        pygame.display.set_caption("Fly-in drone simulation")
        self.clock = pygame.time.Clock()
        self.font: Any = None
        self.title_font: Any = None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            try:
                self.font = pygame.font.Font(None, 24)
                self.title_font = pygame.font.Font(None, 32)
            except (ImportError, RuntimeError):
                # Pygame's font module may be unavailable on minimal installs.
                pass
        self.running = True
        self.s_graph = s_graph
        self.turns = turns
        self.show_capacity = show_capacity
        self.state_tracker = StaticGraphStateTracker(
            drone_paths,
            s_graph,
        )
        self.elapsed = 0.0
        self.current_turn = 0
        self.positions = self._fit_positions()
        self.nodes_by_name = {
            node.name: node for node in self.positions
        }
        self.drone_states = self._build_drone_states(drone_paths)

    def run(self) -> None:
        """Run the animation until the window is closed."""
        while self.running:
            delta = self.clock.tick(60) / 1000.0
            self.elapsed = min(
                self.elapsed + delta,
                self.turns * self._TURN_SECONDS,
            )
            self.current_turn = min(
                int(self.elapsed / self._TURN_SECONDS),
                self.turns,
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill("#20242b")
            self.draw()
            pygame.display.flip()

        pygame.quit()

    def draw(self) -> None:
        """Draw the map, current turn, and all drone positions."""
        self._draw_static_graph()
        self._draw_drones()
        if self.title_font is not None:
            title = self.title_font.render(
                f"Turn {self.current_turn}/{self.turns}",
                True,
                "white",
            )
            self.screen.blit(title, (20, 20))

    def _draw_static_graph(self) -> None:
        """Draw each physical connection and zone once."""
        drawn_links: set[frozenset[str]] = set()
        for edges in self.s_graph.graph.values():
            for edge in edges:
                link = frozenset((edge.from_node.name, edge.to_node.name))
                if link in drawn_links:
                    continue
                drawn_links.add(link)
                pygame.draw.line(
                    self.screen,
                    "#68707c",
                    self.positions[edge.from_node],
                    self.positions[edge.to_node],
                    width=2,
                )

        if self.show_capacity:
            self._draw_capacity_links()

        for node in self.positions:
            pygame.draw.circle(
                self.screen,
                self._node_color(node),
                self.positions[node],
                self._NODE_RADIUS,
            )
            if self.show_capacity:
                self._draw_capacity_zone(node)
            if self.font is not None:
                label = self.font.render(node.name, True, "white")
                label_position = (
                    self.positions[node][0] - label.get_width() / 2,
                    self.positions[node][1] + self._NODE_RADIUS + 4,
                )
                self.screen.blit(label, label_position)

    def _draw_capacity_links(self) -> None:
        """Highlight directed links according to current-turn occupancy."""
        state = self._current_graph_state()
        for edges in self.s_graph.graph.values():
            for edge in edges:
                key = f"link:{edge.from_node.name}-{edge.to_node.name}"
                occupancy = state.get(key, 0)
                if occupancy == 0:
                    continue
                color = self._capacity_color(
                    occupancy,
                    edge.max_link_cap,
                )
                pygame.draw.line(
                    self.screen,
                    color,
                    self.positions[edge.from_node],
                    self.positions[edge.to_node],
                    width=5,
                )

    def _draw_capacity_zone(self, node: Node) -> None:
        """Draw a capacity ring and occupancy label around a zone."""
        state = self._current_graph_state()
        occupancy = state.get(f"zone:{node.name}", 0)
        pygame.draw.circle(
            self.screen,
            self._capacity_color(occupancy, node.max_drones),
            self.positions[node],
            self._NODE_RADIUS + 4,
            width=3,
        )
        if self.font is None:
            return
        capacity = "inf" if node.max_drones > 1000000 else str(node.max_drones)
        label = self.font.render(
            f"{occupancy}/{capacity}",
            True,
            "white",
        )
        self.screen.blit(
            label,
            (
                self.positions[node][0] - label.get_width() / 2,
                self.positions[node][1] - self._NODE_RADIUS - 22,
            ),
        )

    def _current_graph_state(self) -> dict[str, int]:
        """Return occupancy data for the currently displayed turn."""
        turn = min(
            self.current_turn,
            len(self.state_tracker.state_per_turn) - 1,
        )
        return self.state_tracker.state_per_turn[turn]

    @staticmethod
    def _capacity_color(occupancy: int, capacity: int) -> str:
        """Map occupancy level to a capacity indicator color."""
        if capacity > 1000000:
            return "#f4a261" if occupancy else "#68707c"
        if occupancy >= capacity:
            return "#e63946"
        if occupancy > 0:
            return "#f4a261"
        return "#68707c"

    def _draw_drones(self) -> None:
        """Draw drones moving smoothly between consecutive turn states."""
        animation_turn = self.elapsed / self._TURN_SECONDS
        start_turn = min(int(animation_turn), self.turns)
        progress = animation_turn - start_turn

        for drone_id, states in self.drone_states.items():
            start_state = self._state_at(states, start_turn)
            end_state = self._state_at(states, start_turn + 1)
            start_position = self._state_position(start_state)
            end_position = self._state_position(end_state)
            position = (
                start_position[0]
                + (end_position[0] - start_position[0]) * progress,
                start_position[1]
                + (end_position[1] - start_position[1]) * progress,
            )
            if start_state.in_transit or end_state.in_transit:
                color = "#ff9f1c"
            else:
                color = self._drone_color(drone_id)
            pygame.draw.circle(
                self.screen,
                color,
                position,
                self._DRONE_RADIUS,
            )
            if self.font is not None:
                label = self.font.render(f"D{drone_id}", True, "white")
                self.screen.blit(
                    label,
                    (position[0] + 10, position[1] - 10),
                )

    def _fit_positions(self) -> dict[Node, tuple[float, float]]:
        """Scale and center all map coordinates inside the window."""
        nodes: set[Node] = {
            self.s_graph.source_node,
            self.s_graph.sink_node,
        }
        nodes.update(self.s_graph.graph.keys())
        for edges in self.s_graph.graph.values():
            nodes.update(edge.to_node for edge in edges)

        min_x = min(node.x for node in nodes)
        max_x = max(node.x for node in nodes)
        min_y = min(node.y for node in nodes)
        max_y = max(node.y for node in nodes)
        width = max_x - min_x
        height = max_y - min_y
        available_width = self._WIDTH - 2 * self._MARGIN
        available_height = self._HEIGHT - 2 * self._MARGIN - 50
        scale_x = available_width / width if width else available_width
        scale_y = available_height / height if height else available_height
        scale = min(scale_x, scale_y)

        positions: dict[Node, tuple[float, float]] = {}
        for node in nodes:
            x = (
                self._WIDTH / 2
                if not width
                else self._MARGIN + (node.x - min_x) * scale
            )
            y = (
                self._HEIGHT / 2
                if not height
                else self._MARGIN + (node.y - min_y) * scale
            )
            positions[node] = (x, y)
        return positions

    def _build_drone_states(
        self,
        paths: list[list[TEdge]],
    ) -> dict[int, dict[int, DroneState]]:
        """Build physical drone states from decomposed TEG paths."""
        result: dict[int, dict[int, DroneState]] = {}
        for drone_id, path in enumerate(paths, start=1):
            if not path:
                continue
            states = {0: DroneState(path[0].from_node.node)}
            for edge in path:
                from_node = edge.from_node
                to_node = edge.to_node
                if from_node.role != Role.r_out or to_node.role != Role.r_in:
                    continue
                if to_node.node.name == "SUPER_SINK":
                    continue
                if from_node.node.name == to_node.node.name:
                    states[to_node.t] = DroneState(from_node.node)
                elif to_node.node.name.startswith("__TRANSIT__"):
                    destination = self._transit_destination(to_node.node.name)
                    states[to_node.t] = DroneState(
                        from_node.node,
                        from_node.node,
                        destination,
                    )
                else:
                    states[to_node.t] = DroneState(to_node.node)
            result[drone_id] = states
        return result

    def _state_at(
        self,
        states: dict[int, DroneState],
        turn: int,
    ) -> DroneState:
        """Return the latest known state at a particular turn."""
        available_times = [
            time for time in states if time <= turn
        ]
        return states[max(available_times)]

    def _state_position(self, state: DroneState) -> tuple[float, float]:
        """Return the screen position represented by a drone state."""
        if state.in_transit:
            assert state.transit_from is not None
            assert state.transit_to is not None
            start = self.positions[state.transit_from]
            end = self.positions[state.transit_to]
            return ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        return self.positions[state.node]

    def _transit_destination(self, transit_name: str) -> Node:
        """Return the physical destination encoded in a transit name."""
        body = transit_name.removeprefix("__TRANSIT__")
        parts = body.rsplit("__", 1)[0].rsplit("__", 1)
        if len(parts) != 2 or parts[1] not in self.nodes_by_name:
            raise ValueError(f"Invalid transit node: {transit_name}")
        return self.nodes_by_name[parts[1]]

    def _graph_state_print(self, drone_path: list[list[TEdge]]) -> None:
        pass

    @staticmethod
    def _node_color(node: Node) -> str:
        """Return a safe Pygame color for a physical zone."""
        color = node.color or "#4f5968"
        try:
            pygame.Color(color)
            return color
        except ValueError:
            fallback = {
                ZoneType.priority: "#f9c74f",
                ZoneType.restricted: "#f9844a",
                ZoneType.blocked: "#343a40",
            }
            return fallback.get(node.z_type, "#4f5968")

    @staticmethod
    def _drone_color(drone_id: int) -> str:
        """Return a repeatable color for a drone marker."""
        colors = ("#f94144", "#277da1", "#90be6d", "#f9c74f", "#f9844a")
        return colors[(drone_id - 1) % len(colors)]
