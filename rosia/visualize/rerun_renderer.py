import rerun as rr
import rerun.blueprint as rrb

BORDER_WIDTH = 3.0
NODE_FILL_COLOR = [255, 255, 255, 255]
NODE_BORDER_COLOR = [0, 0, 0, 255]
CONNECTION_COLOR = [0, 0, 0, 255]
TEXT_COLOR = [0, 0, 0, 255]


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

            abs_cy = node_y + port_y + port_h / 2.0

            if is_input:
                port_label_positions.append([node_x + 16, abs_cy])
                port_label_texts.append(short_name)
            else:
                right_edge = node_x + node_w
                port_label_positions.append([right_edge - 16, abs_cy])
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


def _render_edges(graph: dict) -> None:
    line_strips = []
    arrow_origins = []
    arrow_vectors = []

    for edge in graph.get("edges", []):
        for section in edge.get("sections", []):
            start = section["startPoint"]
            end = section["endPoint"]
            bends = section.get("bendPoints", [])

            # Build polyline: start -> bends -> end
            points = [[start["x"], start["y"]]]
            for bp in bends:
                points.append([bp["x"], bp["y"]])
            points.append([end["x"], end["y"]])

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
