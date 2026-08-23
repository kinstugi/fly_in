from input_processor import InputProcessor
import sys
from graph_lib import StaticGraph
from solution_engine import SolutionEngine
from teg_decomposer import TEGDecomposer
from formatter import OutputFormatter


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("run code, `python3 main.py <path_to_file>`")
        exit()
    processor = InputProcessor(args[1])
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

    output = OutputFormatter().format(drone_paths, op_time)
    if output:
        print(output)
