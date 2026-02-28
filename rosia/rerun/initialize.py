from typing import Any
import rerun as rr
import rerun.blueprint as rrb

import numpy as np
from PIL import Image

from rosia.config import ExecutionConfig
from rosia.time import Time


class RerunConnector:
    def __init__(self, execution_config: ExecutionConfig):
        self.execution_config = execution_config
        rr.init(
            self.execution_config.rerun_name,
            recording_id=self.execution_config.rerun_recording_id,
            spawn=True,
        )

    def send_blueprint(self) -> None:
        rr.send_blueprint(
            rrb.Blueprint(
                rrb.Spatial2DView(origin="/diagram", background=[255, 255, 255])
            )
        )

    def render_diagram(self, diagram: Image.Image) -> None:
        rr.log("diagram", rr.Image(np.array(diagram)))

    def trace(
        self, node_name: str, logical_time: Time, physical_time: Time, message: Any
    ) -> None:
        if self.execution_config.trace:
            rr.set_time("logical_time", duration=logical_time.to_unix_time())
            rr.set_time("physical_time", duration=physical_time.to_unix_time())
            rr.log(
                f"/trace/{node_name}",
                rr.TextLog(text=str(message), level="DEBUG"),
            )
