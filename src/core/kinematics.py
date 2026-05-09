from __future__ import annotations

import math
from dataclasses import replace

from .types import MotionCommand, MotionState, PrinterConfig


class KinematicsEngine:
    def __init__(self, config: PrinterConfig) -> None:
        self.config = config

    def _clamp(self, value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    def apply(self, state: MotionState, cmd: MotionCommand) -> MotionState:
        next_state = replace(state)
        alarms: list[str] = []

        if cmd.f is not None:
            next_state.feed_rate = self._clamp(cmd.f, 1.0, self.config.max_feed_rate)

        if cmd.kind in {"G0", "G1"}:
            target_x = next_state.x if cmd.x is None else self._clamp(cmd.x, 0.0, self.config.build_x)
            target_y = next_state.y if cmd.y is None else self._clamp(cmd.y, 0.0, self.config.build_y)
            target_z = next_state.z if cmd.z is None else self._clamp(cmd.z, 0.0, self.config.build_z)
            target_e = next_state.e if cmd.e is None else cmd.e

            if cmd.x is not None and target_x != cmd.x:
                alarms.append("X soft-limit hit")
            if cmd.y is not None and target_y != cmd.y:
                alarms.append("Y soft-limit hit")
            if cmd.z is not None and target_z != cmd.z:
                alarms.append("Z soft-limit hit")

            distance = math.dist((next_state.x, next_state.y, next_state.z), (target_x, target_y, target_z))
            speed_mm_s = max(next_state.feed_rate / 60.0, 1e-6)
            dt = distance / speed_mm_s

            next_state.t += dt
            next_state.x = target_x
            next_state.y = target_y
            next_state.z = target_z
            next_state.e = target_e

        next_state.alarms = alarms
        return next_state
