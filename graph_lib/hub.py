from enum import Enum


class Type(Enum):
    priority = 0
    normal = 1
    blocked = 2
    restricted = 3


class Hub:
    def __init__(
        self, name: str,
        x: int, y: int,
        z_type: Type = Type.normal,
        color: str | None = None,
        max_drones: int = 1
    ):
        self.name = name
        self.x = x
        self.y = y
        self.z_type = z_type
        self.color = color
        self.max_drones = max_drones
        self.neigbors: set[Hub] = set()
