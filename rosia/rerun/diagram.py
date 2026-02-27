import numpy as np
import rerun as rr
from PIL import Image


def render_diagram(diagram: Image.Image) -> None:
    rr.log("diagram", rr.Image(np.array(diagram)))
