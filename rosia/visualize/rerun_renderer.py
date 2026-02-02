import rerun as rr
import rerun.blueprint as rrb

BORDER_WIDTH = 3.0
NODE_FILL_COLOR = [255, 255, 255, 255]
NODE_BORDER_COLOR = [0, 0, 0, 255]
CONNECTION_COLOR = [0, 0, 0, 255]
TEXT_COLOR = [0, 0, 0, 255]

# Approximate character width in pixels for text width estimation
CHAR_WIDTH = 6.0
PORT_LABEL_PADDING = 4


def render_diagram(graph: dict) -> None:
    rr.init("rosia_diagram", spawn=True)
    rr.send_blueprint(
        rrb.Blueprint(
            rrb.Spatial2DView(origin="/diagram", background=[255, 255, 255]),
        )
    )

    _render_nodes(graph)
    _render_ports(graph)
    _render_edges(graph)


def _render_nodes(graph: dict) -> None:
    centers = []
    half_sizes = []
    labels = []

    for child in graph.get("children", []):
        x = child["x"]
        y = child["y"]
        w = child["width"]
        h = child["height"]

        cx = x + w / 2.0
        cy = y + h / 2.0

        centers.append([cx, cy])
        half_sizes.append([w / 2.0, h / 2.0])
        labels.append(child.get("_node_name", child["id"]))

    if not centers:
        return

    # Fill layer (white, with node name labels)
    rr.log(
        "diagram/node_fills",
        rr.Boxes2D(
            centers=centers,
            half_sizes=half_sizes,
            colors=[NODE_FILL_COLOR] * len(centers),
            labels=labels,
            draw_order=0.0,
        ),
    )

    # Border layer (black outline, on top)
    rr.log(
        "diagram/node_borders",
        rr.Boxes2D(
            centers=centers,
            half_sizes=half_sizes,
            colors=[NODE_BORDER_COLOR] * len(centers),
            radii=[2.0] * len(centers),
            draw_order=1.0,
        ),
    )


def _estimate_text_width(text: str) -> float:
    """Estimate text width based on character count."""
    return len(text) * CHAR_WIDTH + 2 * PORT_LABEL_PADDING


def _render_ports(graph: dict) -> None:
    port_label_positions = []
    port_label_texts = []

    for child in graph.get("children", []):
        node_x = child["x"]
        node_y = child["y"]
        node_w = child["width"]

        for port in child.get("ports", []):
            port_y = port.get("y", 0)
            port_h = port.get("height", 0)
            is_input = port.get("_is_input", True)
            short_name = port.get("_short_name", "")

            abs_cy = node_y + port_y - port_h / 2.0
            text_width = _estimate_text_width(short_name)

            if is_input:
                # Position label center at padding + half text width from left edge
                port_x = node_x + PORT_LABEL_PADDING + text_width / 2.0
                port_label_positions.append([port_x, abs_cy])
                port_label_texts.append(short_name)
            else:
                right_edge = node_x + node_w
                # Position label center at padding + half text width from right edge
                port_x = right_edge - PORT_LABEL_PADDING - text_width / 2.0
                port_label_positions.append([port_x, abs_cy])
                port_label_texts.append(short_name)

    if port_label_positions:
        rr.log(
            "diagram/port_labels",
            rr.Points2D(
                positions=port_label_positions,
                labels=port_label_texts,
                radii=[0.0] * len(port_label_positions),
                colors=[NODE_FILL_COLOR] * len(port_label_positions),
                draw_order=4.0,
            ),
        )


def _build_port_position_map(graph: dict) -> dict:
    """Build a mapping from port ID to its connection point (x, y) at the node edge."""
    port_positions = {}

    for child in graph.get("children", []):
        node_x = child["x"]
        node_y = child["y"]
        node_w = child["width"]

        for port in child.get("ports", []):
            port_id = port["id"]
            port_y = port.get("y", 0)
            port_h = port.get("height", 0)
            is_input = port.get("_is_input", True)

            # Port center Y position
            abs_cy = node_y + port_y + port_h / 2.0

            if is_input:
                # Connection point at the left edge of the node
                port_x = node_x
            else:
                # Connection point at the right edge of the node
                port_x = node_x + node_w

            port_positions[port_id] = [port_x, abs_cy]

    return port_positions


def _render_edges(graph: dict) -> None:
    # Build port position map
    port_positions = _build_port_position_map(graph)

    line_strips = []
    arrow_origins = []
    arrow_vectors = []

    for edge in graph.get("edges", []):
        # Get source and target port IDs
        sources = edge.get("sources", [])
        targets = edge.get("targets", [])

        if not sources or not targets:
            continue

        source_port_id = sources[0]
        target_port_id = targets[0]

        # Get actual port positions
        source_pos = port_positions.get(source_port_id)
        target_pos = port_positions.get(target_port_id)

        if source_pos is None or target_pos is None:
            continue

        # Get bend points from ELK layout
        bends = []
        for section in edge.get("sections", []):
            bends.extend(section.get("bendPoints", []))

        # Build polyline: source_port -> bends -> target_port
        points = [source_pos]
        for bp in bends:
            points.append([bp["x"], bp["y"]])
        points.append(target_pos)

        # Use LineStrips2D for bend segments, Arrows2D for the final segment
        if len(points) > 2:
            line_strips.append(points[:-1])

        # Final segment as an arrow
        origin = points[-2]
        tip = points[-1]
        arrow_origins.append(origin)
        arrow_vectors.append([tip[0] - origin[0], tip[1] - origin[1]])

    if line_strips:
        rr.log(
            "diagram/connection_lines",
            rr.LineStrips2D(
                strips=line_strips,
                colors=[CONNECTION_COLOR] * len(line_strips),
                radii=[2.0] * len(line_strips),
                draw_order=5.0,
            ),
        )

    if arrow_origins:
        rr.log(
            "diagram/connection_arrows",
            rr.Arrows2D(
                origins=arrow_origins,
                vectors=arrow_vectors,
                colors=[CONNECTION_COLOR] * len(arrow_origins),
                radii=[2.0] * len(arrow_origins),
                draw_order=6.0,
            ),
        )
