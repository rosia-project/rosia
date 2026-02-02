from typing import Dict, TYPE_CHECKING
from elkpy import ELK

if TYPE_CHECKING:
    from rosia.coordinate.Coordinator import NodeRuntimeInfo


def visualize_diagram(node_infos: "Dict[str, NodeRuntimeInfo]") -> None:
    if not node_infos:
        return

    from rosia.visualize.elk_builder import build_elk_graph
    from rosia.visualize.rerun_renderer import render_diagram

    graph = build_elk_graph(node_infos)
    elk = ELK()
    laid_out_graph = elk.layout(graph)
    render_diagram(laid_out_graph)
