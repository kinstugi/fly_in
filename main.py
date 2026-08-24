from input_processor import InputProcessor
import sys
from graph_lib import StaticGraph
from solution_engine import SolutionEngine
from teg_decomposer import TEGDecomposer
from formatter import OutputFormatter


def main() -> int:
    args = sys.argv[1:]
    if len(args) not in [1, 2] or (
        len(args) == 2 and args[1] != "--visual"
    ):
        raise ValueError("usage: python3 main.py <path_to_file>")
    visual = len(args) == 2

    processor = InputProcessor(args[0])
    start_node = processor.nodes.get(processor.start_hub_name)
    end_node = processor.nodes.get(processor.end_hub_name)
    if start_node is None or end_node is None:
        raise ValueError("Input must define valid start and end hubs")

    s_graph = StaticGraph(start_node, end_node)
    for f_node, t_node, cap in processor.edges:
        from_node = processor.nodes.get(f_node)
        to_node = processor.nodes.get(t_node)
        if from_node is None or to_node is None:
            raise ValueError(
                f"Connection references an unknown hub: {f_node}-{t_node}"
            )
        s_graph.add_connection(from_node, to_node, cap)

    engine = SolutionEngine(s_graph, processor.nb_drones)
    op_time, op_teg = engine.find_optimal_time()
    if op_teg is None:
        raise RuntimeError("No route can deliver all drones")

    decomp = TEGDecomposer(op_teg, processor.nb_drones)
    drone_paths = decomp.decompose()
    if len(drone_paths) != processor.nb_drones:
        raise RuntimeError(
            "Flow decomposition did not produce every drone path"
        )

    output = OutputFormatter().format(drone_paths, op_time, visual)
    if output:
        print(output)
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
