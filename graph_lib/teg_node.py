from graph_lib import Node
from enum import Enum
from typing import Any


class Role(Enum):
    r_in = 1
    r_out = 2


class TEGNode:
    def __init__(self, node: Node, t: int, role: Role = Role.r_in):
        self.node = node
        self.t = t
        self.role = role

    def __hash__(self) -> int:
        return hash((self.node.name, self.t, self.role))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TEGNode):
            return (
                other.t == self.t and
                other.node.name == self.node.name and
                other.role == self.role
            )
        return False
