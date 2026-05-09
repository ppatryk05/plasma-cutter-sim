from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from src.core.types import MotionState
from src.sim.simulator import SimulationFrame


def export_frames(path: str | Path, frames: Iterable[SimulationFrame]) -> None:
    data = [
        {
            "t": frame.state.t,
            "x": frame.state.x,
            "y": frame.state.y,
            "z": frame.state.z,
            "e": frame.state.e,
            "feed_rate": frame.state.feed_rate,
            "nozzle_temp": frame.state.nozzle_temp,
            "bed_temp": frame.state.bed_temp,
            "issues": frame.issues,
        }
        for frame in frames
    ]
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def import_frames(path: str | Path) -> List[SimulationFrame]:
    source = json.loads(Path(path).read_text(encoding="utf-8"))
    frames: List[SimulationFrame] = []
    for item in source:
        state = MotionState(
            t=item["t"],
            x=item["x"],
            y=item["y"],
            z=item["z"],
            e=item["e"],
            feed_rate=item["feed_rate"],
            nozzle_temp=item["nozzle_temp"],
            bed_temp=item["bed_temp"],
            alarms=[],
        )
        frames.append(SimulationFrame(state=state, issues=item.get("issues", [])))
    return frames
