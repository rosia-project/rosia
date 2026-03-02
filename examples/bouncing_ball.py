"""3D bouncing ball on a surface visualized with rerun.

Pipeline:
  Timer -> PhysicsSimulator -> Renderer

The PhysicsSimulator integrates gravity and handles elastic
bounces off the ground plane (z=0).  The Renderer logs the ball
position and the ground grid to the rerun 3D viewer each tick.

Only uses numpy — no other scientific libraries required.
"""

import numpy as np
import rerun as rr

from rosia import InputPort, OutputPort, reaction, Node, Coordinator
from rosia import request_shutdown, log
from rosia.time import s, ms, Time
from rosia.time.Timer import Timer


class BallState:
    """Position + velocity of the ball, streamable to rerun."""

    def __init__(self, position: np.ndarray, velocity: np.ndarray) -> None:
        self.position = position  # (3,)
        self.velocity = velocity  # (3,)

    def to_rerun(self) -> rr.Points3D:
        return rr.Points3D(
            [self.position],
            radii=[0.3],
            colors=[[255, 100, 50]],
        )

    def __repr__(self) -> str:
        x, y, z = self.position
        return f"pos=({x:.2f}, {y:.2f}, {z:.2f})"


@Node
class PhysicsSimulator:
    """Simulates a ball under gravity with elastic bounces off z=0."""

    tick = InputPort[Time]()
    output = OutputPort[BallState]()

    def __init__(
        self,
        initial_position: tuple[float, float, float] = (0.0, 0.0, 5.0),
        initial_velocity: tuple[float, float, float] = (2.0, 1.5, 0.0),
        gravity: float = -9.81,
        restitution: float = 0.85,
        dt: float = 0.02,
        max_ticks: int = 500,
    ):
        self.position = np.array(initial_position, dtype=float)
        self.velocity = np.array(initial_velocity, dtype=float)
        self.gravity = gravity
        self.restitution = restitution
        self.dt = dt
        self.max_ticks = max_ticks
        self.tick_count = 0

    @reaction([tick])
    def step(self):
        # Apply gravity (z-axis is up)
        self.velocity[2] += self.gravity * self.dt
        self.position += self.velocity * self.dt

        # Bounce off ground plane z=0
        if self.position[2] <= 0.0:
            self.position[2] = -self.position[2]
            self.velocity[2] = -self.velocity[2] * self.restitution

        self.output(BallState(self.position.copy(), self.velocity.copy()))
        self.tick_count += 1
        if self.tick_count >= self.max_ticks:
            request_shutdown(0 * s)


@Node
class Renderer:
    """Logs ball position and ground plane to rerun."""

    input_state = InputPort[BallState]()

    def start(self):
        lines = []
        for i in np.linspace(-5, 15, 21):
            lines.append([[i, -5, 0], [i, 15, 0]])
            lines.append([[-5, i, 0], [15, i, 0]])
        log.rerun(
            rr.LineStrips3D(lines, colors=[[200, 200, 200]]),
            rerun_subpath="ground",
        )
        log.info("ground plane logged")

    @reaction([input_state])
    def render(self):
        log.info(f"ball {self.input_state}")


if __name__ == "__main__":
    coor = Coordinator()

    timer = coor.create_node(Timer(interval=20 * ms, offset=0 * s))
    sim = coor.create_node(PhysicsSimulator())
    renderer = coor.create_node(Renderer())

    timer.output_timer >>= sim.tick
    sim.output >>= renderer.input_state

    coor.diagram()
    coor.execute(trace=True, log_level="INFO")
