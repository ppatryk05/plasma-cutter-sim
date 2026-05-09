from __future__ import annotations

from dataclasses import replace

from .types import MotionCommand, MotionState


class ThermalModel:
    def __init__(self, ambient: float = 25.0, heat_rate: float = 2.8, cool_rate: float = 0.25) -> None:
        self.ambient = ambient
        self.heat_rate = heat_rate
        self.cool_rate = cool_rate
        self.target_nozzle = ambient
        self.target_bed = ambient

    def _step_towards(self, value: float, target: float, dt: float) -> float:
        if value < target:
            return min(target, value + self.heat_rate * dt)
        if value > target:
            return max(target, value - self.cool_rate * dt)
        return value

    def apply(self, state: MotionState, cmd: MotionCommand, dt: float) -> MotionState:
        next_state = replace(state)
        if cmd.nozzle_temp is not None:
            self.target_nozzle = cmd.nozzle_temp
        if cmd.bed_temp is not None:
            self.target_bed = cmd.bed_temp

        next_state.nozzle_temp = self._step_towards(next_state.nozzle_temp, self.target_nozzle, dt)
        next_state.bed_temp = self._step_towards(next_state.bed_temp, self.target_bed, dt)
        return next_state
