*This project has been created as part of the 42 curriculum by bkusi-fr.*

# Fly-in

## Description

Fly-in is a drone-routing simulation. The program reads a map of connected
zones and calculates a schedule that moves all drones from a start zone to an
end zone in the fewest possible simulation turns.

The map supports:

- Zone occupancy capacities.
- Connection capacities.
- Normal movement with a one-turn cost.
- Restricted zones with a two-turn movement cost.
- Blocked zones that cannot be entered.
- Waiting and simultaneous drone movement.

The implementation uses a time-expanded graph, Dinic's maximum-flow algorithm,
and binary search over the number of simulation turns.

## Instructions

Run the program with a map file:

```bash
python3 main.py path/to/map.txt
```

For example:

```bash
python3 main.py maps/easy/01_linear_path.txt
```

For colored outputs add --visual

```bash
python3 main.py maps/easy/01_linear_path.txt --visual
```

The program outputs one line per simulation turn. Each movement uses the
required format:

```text
D<ID>-<destination-zone>
```

During restricted-zone transit, the connection is displayed instead of the
destination until the drone arrives.

## Algorithm

For a candidate number of turns `T`, the program builds a time-expanded graph
with layers from time `0` through time `T`.

Each physical zone is split into two nodes at every time:

```text
zone@time_in -> zone@time_out
```

The capacity of this edge represents the maximum number of drones that may
occupy the zone at that time.

The graph also contains:

- Movement edges from time `t` to `t + 1`.
- Transit nodes for movement into restricted zones.
- Waiting edges from a zone at time `t` to the same zone at `t + 1`.
- A source at `START@0_in`.
- A super-sink collecting arrivals at every END time layer.

Dinic's algorithm repeatedly builds a residual level graph and pushes a
blocking flow through it. The resulting maximum flow is the number of drones
that can reach the end within the candidate time horizon.

The solution engine binary-searches the smallest `T` for which:

```text
maximum_flow >= number_of_drones
```

Finally, the flow in the optimal time-expanded graph is decomposed into
individual source-to-sink paths and converted into turn-by-turn drone output.

## Project Structure

```text
graph_lib/
    node.py                 Physical zones and zone types
    edge.py                 Static map connections
    static_graph.py         Physical map graph
    teg_node.py             Time-expanded graph nodes
    teg_edge.py             Flow and residual edges
    time_extended_graph.py  Time-expanded graph construction

input_processor.py          Map parser and validation
solution_engine.py          Binary search for the optimal horizon
teg_decomposer.py           Flow-path decomposition
formatter.py                Turn-by-turn output formatting
main.py                     Application entry point
```

## Output Example

For multiple drones sharing a path, output may look like:

```text
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

Drones that wait during a turn are omitted from that turn's movement line.

## Testing

The repository contains maps grouped by difficulty:

```text
maps/easy/
maps/medium/
maps/hard/
maps/challenger/
```

Begin with the easy maps, then test capacity bottlenecks, loops, restricted
zones, blocked zones, and multiple paths.

Useful checks include:

```bash
python3 main.py maps/easy/01_linear_path.txt
python3 main.py maps/easy/02_simple_fork.txt
python3 -m compileall .
flake8 .
mypy . --warn-return-any --warn-unused-ignores \
    --ignore-missing-imports --disallow-untyped-defs \
    --check-untyped-defs
```

## Design Notes

The static graph contains only physical map information. Flow state, residual
edges, and time information belong to the time-expanded graph. Dinic operates
only on the flow network and does not contain Fly-in-specific rules.

The decomposer consumes the solved flow from the optimal time-expanded graph.
It extracts at most the requested number of drone paths and removes each
extracted flow unit from the network.

## Resources

- E. W. Dijkstra, "A note on two problems in connexion with graphs."
- Yefim Dinitz, the blocking-flow maximum-flow algorithm.
- Cormen, Leiserson, Rivest, and Stein, *Introduction to Algorithms*, chapters
  on maximum flow.
- The Fly-in project subject and its movement, capacity, and output rules.
- [Dinic Video explanation](https://youtu.be/M6cm8UeeziI)
- [Searching with time](https://youtu.be/gUNOdyI0ii0)

AI assistance was used as a review and learning aid for the time-expanded
graph design, Dinic invariants, flow decomposition, parser validation, and
project organization. All generated suggestions were reviewed, tested, and
adapted to the project's own data structures.
