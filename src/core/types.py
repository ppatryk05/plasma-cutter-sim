from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(slots=True)
class MotionCommand:
    kind: str
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    e: Optional[float] = None
    f: Optional[float] = None
    nozzle_temp: Optional[float] = None
    bed_temp: Optional[float] = None


@dataclass(slots=True)
class MotionState:
    t: float = 0.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    e: float = 0.0
    feed_rate: float = 1800.0
    nozzle_temp: float = 25.0
    bed_temp: float = 25.0
    alarms: List[str] = field(default_factory=list)


@dataclass(slots=True)
class PrinterConfig:
    build_x: float = 220.0
    build_y: float = 220.0
    build_z: float = 250.0
    max_feed_rate: float = 7200.0
    max_accel: float = 3000.0
    nozzle_clearance: float = 18.0
