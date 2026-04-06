"""Atari Skiing with a heuristic agent using Rosia.

Pipeline:
  Environment <-> Agent

The Environment wraps gymnasium's Skiing-v5.
The Agent uses a simple angle-tracking heuristic to steer through gates.

Based on: https://github.com/ercardenas/ski-master/blob/master/train_heuristic.py

Requirements:
pip install 'gymnasium[atari]' 'ale-py' 'autorom[accept-rom-license]'
"""

import numpy as np
import gymnasium as gym
import ale_py
from dataclasses import dataclass


import rerun as rr
import rerun.blueprint as rrb

from rosia import InputPort, OutputPort, reaction, Node, Application
from rosia import request_shutdown, log
from rosia.config import RerunConfig
from rosia.time import s


gym.register_envs(ale_py)


@dataclass
class Observation:
    frame: np.ndarray  # (210, 160, 3) RGB image
    reward: float
    done: bool


@dataclass
class Action:
    action: int  # 0=NOOP, 1=RIGHT, 2=LEFT


# Colors in RGB
PLAYER_COLOR = np.array([214, 92, 92])
RED_FLAG_COLOR = np.array([184, 50, 50])
BLUE_FLAG_COLOR = np.array([66, 72, 200])
THETA_DIFF_THRESHOLD = 0.015


def find_position(frame: np.ndarray, color: np.ndarray) -> tuple[float, float] | None:
    """Find mean position of pixels matching color. Returns (row, col) or None."""
    mask = np.all(frame == color, axis=2)
    positions = np.argwhere(mask)
    if len(positions) == 0:
        return None
    return float(positions[:, 0].mean()), float(positions[:, 1].mean())


def find_flag(frame: np.ndarray) -> tuple[float, float] | None:
    """Find the next flag gate (red or blue)."""
    cropped = frame[:200]
    pos = find_position(cropped, RED_FLAG_COLOR)
    if pos is None:
        pos = find_position(cropped, BLUE_FLAG_COLOR)
    return pos


@Node
class Environment:
    observation = OutputPort[Observation]()
    action_in = InputPort[Action]()

    def __init__(self, render: bool = True):
        self.render = render

    def start(self):
        render_mode = "rgb_array" if self.render else None
        self.env = gym.make("ALE/Skiing-v5", render_mode=render_mode)
        frame, _ = self.env.reset()
        log.info("Game started")
        self.observation(
            Observation(
                frame=frame,
                reward=0.0,
                done=False,
            )
        )

    @reaction([action_in])
    def on_action(self):
        action = self.action_in
        frame, reward, terminated, truncated, _ = self.env.step(action.action)
        done = terminated or truncated

        yield 1 * s / 15

        self.observation(
            Observation(
                frame=frame,
                reward=float(reward),
                done=done,
            )
        )

        if done:
            log.info("Game over!")
            self.env.close()
            request_shutdown(0 * s)

    def shutdown(self):
        if hasattr(self, "env"):
            self.env.close()


@Node
class Agent:
    observation_in = InputPort[Observation]()
    action_out = OutputPort[Action]()

    def __init__(self):
        self.prev_theta = 0.0
        self.step_count = 0

    @reaction([observation_in])
    def decide(self):
        obs = self.observation_in
        if obs.done:
            return

        frame = obs.frame
        player_pos = find_position(frame, PLAYER_COLOR)
        flag_pos = find_flag(frame)

        if player_pos is None or flag_pos is None:
            # Can't see player or flag, go straight
            self.action_out(Action(action=0))
            return

        player_row, player_col = player_pos
        flag_row, flag_col = flag_pos

        theta = np.arctan2(flag_row - player_row, flag_col - player_col)
        theta_diff = theta - self.prev_theta
        self.prev_theta = theta

        if theta_diff > THETA_DIFF_THRESHOLD:
            action = 2  # LEFT
        elif theta_diff < -THETA_DIFF_THRESHOLD:
            action = 1  # RIGHT
        else:
            action = 0  # NOOP

        self.step_count += 1

        log.rerun(rr.Image(frame), rerun_subpath="game")
        # rosia.advance_time(1 * s / 15)
        self.action_out(Action(action=action))


if __name__ == "__main__":
    app = Application()
    env = app.create_node(Environment(render=True))
    agent = app.create_node(Agent())

    env.observation >>= agent.observation_in
    agent.action_out >>= env.action_in

    app.diagram()
    app.execute(
        rerun_config=RerunConfig(
            name="skiing",
            blueprint=rrb.Blueprint(rrb.Spatial2DView()),
        )
    )
