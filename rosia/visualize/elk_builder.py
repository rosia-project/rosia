from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from rosia.coordinate.Coordinator import NodeRuntimeInfo

CHAR_WIDTH = 16.0
PORT_ROW_HEIGHT = 48.0
NODE_PADDING_TOP = 60.0
NODE_PADDING_BOTTOM = 20.0
NODE_PADDING_HORIZONTAL = 30.0
PORT_GAP = 60.0
MIN_NODE_WIDTH = 240.0
MIN_NODE_HEIGHT = 100.0


def _compute_node_size(
    node_name: str,
    input_ports: List[dict],
    output_ports: List[dict],
) -> Tuple[float, float]:
    max_port_count = max(len(input_ports), len(output_ports), 1)
    node_height = (
        NODE_PADDING_TOP + max_port_count * PORT_ROW_HEIGHT + NODE_PADDING_BOTTOM
    )

    name_width = len(node_name) * CHAR_WIDTH + 2 * NODE_PADDING_HORIZONTAL

    max_input_name_len = max((len(p["_short_name"]) for p in input_ports), default=0)
    max_output_name_len = max((len(p["_short_name"]) for p in output_ports), default=0)
    port_width = (
        max_input_name_len * CHAR_WIDTH
        + PORT_GAP
        + max_output_name_len * CHAR_WIDTH
        + 2 * NODE_PADDING_HORIZONTAL
    )

    node_width = max(name_width, port_width, MIN_NODE_WIDTH)
    node_height = max(node_height, MIN_NODE_HEIGHT)

    return node_width, node_height


def build_elk_graph(node_infos: "Dict[str, NodeRuntimeInfo]") -> dict:
    children = []
    edges = []
    edge_counter = 0

    for node_name, node_info in node_infos.items():
        node_runtime = node_info.node

        input_ports = []
        for (
            port_full_name,
            port_connector,
        ) in node_runtime.input_port_connectors.items():
            short_name = port_full_name.split(".", 1)[1]
            input_ports.append(
                {
                    "id": port_full_name,
                    "width": 10,
                    "height": 10,
                    "layoutOptions": {"elk.port.side": "WEST"},
                    "_short_name": short_name,
                    "_is_input": True,
                }
            )

        output_ports = []
        for (
            port_full_name,
            port_connector,
        ) in node_runtime.output_port_connectors.items():
            short_name = port_full_name.split(".", 1)[1]
            output_ports.append(
                {
                    "id": port_full_name,
                    "width": 10,
                    "height": 10,
                    "layoutOptions": {"elk.port.side": "EAST"},
                    "_short_name": short_name,
                    "_is_input": False,
                }
            )

        node_width, node_height = _compute_node_size(
            node_name, input_ports, output_ports
        )

        child = {
            "id": node_name,
            "width": node_width,
            "height": node_height,
            "ports": input_ports + output_ports,
            "layoutOptions": {"elk.portConstraints": "FIXED_SIDE"},
            "_node_name": node_name,
        }
        children.append(child)

        for (
            port_full_name,
            port_connector,
        ) in node_runtime.output_port_connectors.items():
            for downstream_input in port_connector.downstream_ports:
                edge_id = f"e{edge_counter}"
                edge_counter += 1
                edges.append(
                    {
                        "id": edge_id,
                        "sources": [port_full_name],
                        "targets": [downstream_input.name],
                    }
                )

    graph = {
        "id": "root",
        "layoutOptions": {
            "elk.algorithm": "layered",
            "elk.direction": "RIGHT",
            "elk.spacing.nodeNode": "60",
            "elk.layered.spacing.nodeNodeBetweenLayers": "120",
        },
        "children": children,
        "edges": edges,
    }
    return graph
