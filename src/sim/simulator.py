from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Generator, List

from src.core.kinematics import KinematicsEngine
from src.core.material_model import MaterialDeposition
from src.core.thermal_model import ThermalModel
from src.core.types import MotionCommand, MotionState, PrinterConfig
from src.sim.collision import CollisionDetector

STEP_MM = 1.0  # one visual frame per mm of movement


@dataclass(slots=True)
class SimulationFrame:
    state: MotionState
    issues: list[str]


def _lerp_states(prev: MotionState, nxt: MotionState, steps: int) -> Generator[MotionState, None, None]:
    """Yield `steps` linearly-interpolated intermediate states from prev→nxt."""
    for i in range(1, steps + 1):
        t = i / steps
        yield replace(
            nxt,
            x=prev.x + t * (nxt.x - prev.x),
            y=prev.y + t * (nxt.y - prev.y),
            z=prev.z + t * (nxt.z - prev.z),
            e=prev.e + t * (nxt.e - prev.e),
            t=prev.t + t * (nxt.t - prev.t),
        )


class PrinterSimulator:
    def __init__(self, config: PrinterConfig | None = None) -> None:
        self.config = config or PrinterConfig()
        self.kinematics = KinematicsEngine(self.config)
        self.thermal = ThermalModel()
        self.material = MaterialDeposition()
        self.collision = CollisionDetector(self.config)
        self.frames: List[SimulationFrame] = []

    def run(self, commands: List[MotionCommand]) -> List[SimulationFrame]:
        self.frames.clear()
        self.material.clear()
        prev = MotionState()
        self.frames.append(SimulationFrame(state=prev, issues=[]))

        for cmd in commands:
            moved = self.kinematics.apply(prev, cmd)
            dt = max(moved.t - prev.t, 0.01)
            next_state = self.thermal.apply(moved, cmd, dt)
            issues = next_state.alarms + self.collision.check(next_state)

            if cmd.kind in {"G0", "G1"}:
                distance = math.dist(
                    (prev.x, prev.y, prev.z),
                    (next_state.x, next_state.y, next_state.z),
                )
                steps = max(1, int(distance / STEP_MM))
                for interp in _lerp_states(prev, next_state, steps):
                    self.material.update(prev, interp)
                    self.frames.append(SimulationFrame(state=interp, issues=issues))
                    prev = interp
            else:
                self.material.update(prev, next_state)
                self.frames.append(SimulationFrame(state=next_state, issues=issues))
                prev = next_state

        return self.frames
