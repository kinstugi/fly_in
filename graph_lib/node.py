from enum import Enum
from typing import Any


class ZoneType(Enum):
    priority = 0
    normal = 1
    blocked = 2
    restricted = 3


class Node:
    def __init__(
        self, name: str,
        x: int, y: int,
        z_type: ZoneType = ZoneType.normal,
        color: str | None = None,
        max_drones: int = 1
    ):
        self.name = name
        self.x = x
        self.y = y
        self.z_type = z_type
        self.color = color
        self.max_drones = max_drones

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, value: Any):
        if isinstance(value, Node):
            return self.name == value.name
        elif isinstance(value, str):
            return self.name == value
        return False
