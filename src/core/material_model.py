from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .types import MotionState

Point3 = Tuple[float, float, float]
Segment3 = Tuple[Point3, Point3]


@dataclass(slots=True)
class MaterialDeposition:
    min_extrusion_delta: float = 0.0001
    segments: List[Segment3] = field(default_factory=list)

    def update(self, previous: MotionState, current: MotionState) -> None:
        e_delta = current.e - previous.e
        if e_delta > self.min_extrusion_delta:
            self.segments.append(
                ((previous.x, previous.y, previous.z), (current.x, current.y, current.z))
            )

    def clear(self) -> None:
        self.segments.clear()
