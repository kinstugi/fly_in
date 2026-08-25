from collections import defaultdict
import sys

from .edge import Edge
from .node import Node, ZoneType
from .static_graph import StaticGraph
from .teg_edge import SharedCapacity, TEGEdge
from .teg_node import Role, TEGNode


class TimeExtendedGraph:
    """Residual-ready time-expanded network for the ordinary Fly-in rules.

    A physical zone is split into an ``in`` and an ``out`` node at every
    time.  Flow through the split edge represents occupying that zone at
    that time.  Movement and waiting edges always move from time ``t`` to a
    later time, so a path through this graph is also a valid timeline.

    Restricted-zone movement is represented with a synthetic transit zone.
    Entering a restricted destination takes two turns; leaving a restricted
    zone still takes one turn.  Transit nodes are not physical zones and do
    not have waiting edges.
    """

    def __init__(self, turns: int, s_graph: StaticGraph):
        self.turns = turns
        self.graph: defaultdict[TEGNode, list[TEGEdge]] = defaultdict(list)
        self.link_capacity_groups: dict[
            tuple[frozenset[str], int], SharedCapacity
        ] = {}

        # The source is a real TEG node, not a separate super-source.
        self.source_node = TEGNode(s_graph.source_node, 0, Role.r_in)

        # END can be reached at different times, so all arrival times feed
        # one artificial sink.  t=-1 marks this as outside the time layers.
        self.super_sink = TEGNode(
            Node("SUPER_SINK", x=-1, y=-1, max_drones=sys.maxsize),
            -1,
            Role.r_in,
        )
        self.sink_node = self.super_sink

        self.build_graph(s_graph)

    def build_graph(self, s_graph: StaticGraph) -> None:
        # Include endpoints even when an input graph has an isolated start or
        # end node and therefore does not contain it as a dictionary key.
        physical_nodes: set[Node] = {
            s_graph.source_node,
            s_graph.sink_node,
        }
        physical_nodes.update(s_graph.graph.keys())
        for edges in s_graph.graph.values():
            physical_nodes.update(edge.to_node for edge in edges)

        # A blocked zone is not usable.  Filtering here keeps the static graph
        # as a description of the input map while keeping blocked zones out
        # of the flow network.
        usable_nodes = {
            node for node in physical_nodes
            if node.z_type != ZoneType.blocked
        }

        # Create the zone-capacity edges for every time layer.
        for t in range(self.turns + 1):
            for node in usable_nodes:
                node_in = TEGNode(node, t, Role.r_in)
                node_out = TEGNode(node, t, Role.r_out)

                if node in (s_graph.source_node, s_graph.sink_node):
                    capacity = sys.maxsize
                else:
                    capacity = node.max_drones
                self.add_flow_edge(node_in, node_out, capacity)

            # A drone may finish at any positive time up to the horizon.
            # There is no useful END@0 arrival when source and sink differ.
            if t > 0 and s_graph.sink_node in usable_nodes:
                end_out = TEGNode(s_graph.sink_node, t, Role.r_out)
                self.add_flow_edge(end_out, self.super_sink, sys.maxsize)

        # Build movement and waiting edges for each time interval.
        for from_node in physical_nodes:
            if from_node not in usable_nodes or from_node == s_graph.sink_node:
                continue

            # Every static adjacency is directed here.  StaticGraph already
            # stores both directions for a bidirectional connection.
            for edge in s_graph.graph.get(from_node, []):
                if edge.to_node not in usable_nodes:
                    continue
                self._add_movement_edges(edge, from_node)

            for t in range(self.turns):
                from_t = TEGNode(from_node, t, Role.r_out)
                to_t = TEGNode(from_node, t + 1, Role.r_in)

                # START can hold an unlimited number of waiting drones.  A
                # normal or restricted zone uses its occupancy capacity.
                capacity = (
                    sys.maxsize
                    if from_node == s_graph.source_node
                    else from_node.max_drones
                )
                self.add_flow_edge(from_t, to_t, capacity)

    def _add_movement_edges(self, edge: Edge, from_node: Node) -> None:
        """Add all time copies of one static directed connection.

        Normal movement consumes one turn.  When the destination is
        restricted, a synthetic transit zone is inserted at the intermediate
        time, making the movement consume two turns:

            A@t_out -> transit@t+1_in -> transit@t+1_out -> B@t+2_in

        The transit split has link capacity, so at most that many drones can
        be in this directed connection's transit state at once.  There are
        no waiting edges from transit nodes: entering transit commits the
        drone to completing the movement.
        """
        destination = edge.to_node
        capacity = edge.max_link_cap

        for t in range(self.turns):
            from_t = TEGNode(from_node, t, Role.r_out)

            if destination.z_type == ZoneType.restricted:
                arrival_t = t + 2
                if arrival_t > self.turns:
                    continue

                transit_physical = Node(
                    f"__TRANSIT__{from_node.name}__{destination.name}__{t}",
                    x=-1,
                    y=-1,
                    max_drones=capacity,
                )
                transit_in = TEGNode(transit_physical, t + 1, Role.r_in)
                transit_out = TEGNode(transit_physical, t + 1, Role.r_out)
                destination_in = TEGNode(destination, arrival_t, Role.r_in)

                self.add_flow_edge(from_t, transit_in, capacity)
                shared_capacity = self._link_capacity_group(
                    from_node,
                    destination,
                    t + 1,
                    capacity,
                )
                self.add_flow_edge(
                    transit_in,
                    transit_out,
                    capacity,
                    shared_capacity,
                )
                self.add_flow_edge(transit_out, destination_in, capacity)
            else:
                destination_in = TEGNode(destination, t + 1, Role.r_in)
                shared_capacity = self._link_capacity_group(
                    from_node,
                    destination,
                    t,
                    capacity,
                )
                self.add_flow_edge(
                    from_t,
                    destination_in,
                    capacity,
                    shared_capacity,
                )

    def _link_capacity_group(
        self,
        from_node: Node,
        to_node: Node,
        turn: int,
        capacity: int,
    ) -> SharedCapacity:
        """Return one capacity group for both directions of a link/time."""
        link = frozenset((from_node.name, to_node.name))
        key = (link, turn)
        if key not in self.link_capacity_groups:
            self.link_capacity_groups[key] = SharedCapacity(capacity)
        return self.link_capacity_groups[key]

    def add_flow_edge(
        self,
        from_node: TEGNode,
        to_node: TEGNode,
        capacity: int,
        shared_capacity: SharedCapacity | None = None,
    ) -> None:
        """Insert one capacity edge and its zero-capacity residual reverse."""
        forward_edge = TEGEdge(
            from_node,
            to_node,
            capacity,
            shared_capacity,
        )
        reverse_edge = TEGEdge(
            to_node,
            from_node,
            0,
            shared_capacity,
            shared_direction=-1,
        )

        forward_edge.reverse_edge = reverse_edge
        reverse_edge.reverse_edge = forward_edge

        self.graph[from_node].append(forward_edge)
        self.graph[to_node].append(reverse_edge)
