"""Rerun-specific rendering for displaying graphs in the rerun viewer."""

from typing import TYPE_CHECKING

import numpy as np
import rerun as rr
import rerun.blueprint as rrb

from rosia.diagram.renderer import render_graph

if TYPE_CHECKING:
    from rosia.diagram.diagram import Graph


def render_to_rerun(graph: "Graph", rerun_name: str, rerun_recording_id: str) -> None:
    """Render a graph and display it in rerun."""
    rr.init(rerun_name, recording_id=rerun_recording_id, spawn=True)
    rr.send_blueprint(
        rrb.Blueprint(rrb.Spatial2DView(origin="/diagram", background=[255, 255, 255]))
    )

    img = render_graph(graph)
    rr.log("diagram", rr.Image(np.array(img)))
