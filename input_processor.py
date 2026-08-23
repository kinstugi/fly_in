import re
from typing import NoReturn

from graph_lib import Node, ZoneType


class InputProcessor:
    """Parse and validate a Fly-in map file."""

    _HUB_METADATA = {"zone", "color", "max_drones"}
    _CONNECTION_METADATA = {"max_link_capacity"}

    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.nb_drones = 0
        self.start_hub_name = ""
        self.end_hub_name = ""
        self.nodes: dict[str, Node] = {}
        self.edges: list[tuple[str, str, int]] = []
        self._connections: set[frozenset[str]] = set()
        self.process_file()

    def process_file(self) -> None:
        """Read, parse, and validate the complete input file."""
        try:
            with open(self.file_path, "r") as fh:
                first_data_line = True
                for line_number, raw_line in enumerate(fh, start=1):
                    line = raw_line.split("#", 1)[0].strip()
                    if not line:
                        continue

                    key, separator, value = line.partition(":")
                    if not separator:
                        self._error(line_number, "missing ':' separator")

                    key = key.strip().lower()
                    value = value.strip()

                    if first_data_line and key != "nb_drones":
                        self._error(
                            line_number,
                            "the first data line must define nb_drones",
                        )
                    first_data_line = False

                    if key == "nb_drones":
                        self._parse_num_drones(value, line_number)
                    elif key in {"start_hub", "end_hub", "hub"}:
                        self._parse_hub(key, value, line_number)
                    elif key == "connection":
                        self._parse_connection(value, line_number)
                    else:
                        self._error(line_number, f"unknown directive '{key}'")
        except OSError as exc:
            raise ValueError(f"Cannot read '{self.file_path}': {exc}") from exc

        if first_data_line:
            raise ValueError("Input file is empty")
        if not self.start_hub_name or not self.end_hub_name:
            raise ValueError(
                "Input must contain exactly one start_hub and one end_hub"
            )

    def _parse_num_drones(self, value: str, line_number: int) -> None:
        if self.nb_drones != 0:
            self._error(line_number, "duplicate nb_drones definition")
        if not re.fullmatch(r"[1-9][0-9]*", value):
            self._error(line_number, "nb_drones must be a positive integer")
        self.nb_drones = int(value)

    def _parse_hub(self, kind: str, value: str, line_number: int) -> None:
        parts = value.split(maxsplit=3)
        if len(parts) not in {3, 4}:
            self._error(
                line_number,
                "hub must have name, x, y, and optional metadata",
            )

        name, x_value, y_value = parts[:3]
        if "-" in name or not re.fullmatch(r"[^\s:\[\]]+", name):
            self._error(
                line_number,
                "hub names cannot contain spaces, ':' or '-'",
            )
        if name in self.nodes:
            self._error(line_number, f"duplicate hub name '{name}'")

        try:
            x = int(x_value)
            y = int(y_value)
        except ValueError:
            self._error(line_number, "hub coordinates must be integers")

        metadata = self._parse_metadata(
            parts[3] if len(parts) == 4 else None,
            self._HUB_METADATA,
            line_number,
        )
        node = Node(name, x, y)

        if "zone" in metadata:
            try:
                node.z_type = ZoneType[metadata["zone"]]
            except ValueError:
                self._error(
                    line_number,
                    f"invalid zone type '{metadata['zone']}'",
                )
        if "color" in metadata:
            node.color = metadata["color"]
        if "max_drones" in metadata:
            node.max_drones = self._positive_int(
                metadata["max_drones"],
                line_number,
                "max_drones",
            )

        self.nodes[name] = node
        if kind == "start_hub":
            if self.start_hub_name:
                self._error(line_number, "duplicate start_hub")
            self.start_hub_name = name
        elif kind == "end_hub":
            if self.end_hub_name:
                self._error(line_number, "duplicate end_hub")
            self.end_hub_name = name

    def _parse_connection(self, value: str, line_number: int) -> None:
        parts = value.split(maxsplit=1)
        connection = parts[0]
        if connection.count("-") != 1:
            self._error(
                line_number,
                "connection must have exactly two hub names",
            )

        from_name, to_name = connection.split("-")
        if from_name not in self.nodes or to_name not in self.nodes:
            self._error(
                line_number,
                "connections may only reference previously defined hubs",
            )
        if from_name == to_name:
            self._error(line_number, "a connection cannot connect a hub to itself")

        connection_key = frozenset((from_name, to_name))
        if connection_key in self._connections:
            self._error(line_number, "duplicate connection")

        metadata = self._parse_metadata(
            parts[1] if len(parts) == 2 else None,
            self._CONNECTION_METADATA,
            line_number,
        )
        capacity = self._positive_int(
            metadata.get("max_link_capacity", "1"),
            line_number,
            "max_link_capacity",
        )
        self._connections.add(connection_key)
        self.edges.append((from_name, to_name, capacity))

    def _parse_metadata(
        self,
        value: str | None,
        allowed_keys: set[str],
        line_number: int,
    ) -> dict[str, str]:
        if value is None:
            return {}
        if not (value.startswith("[") and value.endswith("]")):
            self._error(
                line_number,
                "metadata must be enclosed in '[' and ']'",
            )

        content = value[1:-1].strip()
        if not content:
            self._error(line_number, "metadata cannot be empty")

        metadata: dict[str, str] = {}
        for item in content.split():
            if item.count("=") != 1:
                self._error(line_number, f"invalid metadata item '{item}'")
            key, item_value = item.split("=", 1)
            key = key.lower()
            if key not in allowed_keys:
                self._error(line_number, f"unknown metadata key '{key}'")
            if key in metadata:
                self._error(line_number, f"duplicate metadata key '{key}'")
            if not item_value:
                self._error(
                    line_number,
                    f"metadata value for '{key}' is empty",
                )
            metadata[key] = item_value.lower() if key == "zone" else item_value
        return metadata

    def _positive_int(self, value: str, line_number: int, field: str) -> int:
        if not re.fullmatch(r"[1-9][0-9]*", value):
            self._error(line_number, f"{field} must be a positive integer")
        return int(value)

    @staticmethod
    def _error(line_number: int, message: str) -> NoReturn:
        raise ValueError(f"Line {line_number}: {message}")
