"""CutterMachine – top-level simulation coordinator.

Owns PlasmaHead, SheetMetal, and PathRecorder and exposes a single
``update()`` method that the main loop calls once per frame.
"""

from __future__ import annotations

import math

import pygame

from core.path_recorder import PathRecorder
from core.plasma_head import PlasmaHead
from core.sheet_metal import SheetMetal


class CutterMachine:
    """Coordinates the plasma-cutter simulation components.

    Speed modifiers (applied while the key is held):
        Shift  – boost to 400 mm/s
        Ctrl   – precision at 80 mm/s
        (none) – normal 200 mm/s
    """

    _SPEED_NORMAL    = 200.0   # mm/s
    _SPEED_BOOST     = 400.0   # mm/s
    _SPEED_PRECISION = 80.0    # mm/s

    def __init__(self) -> None:
        self.head     = PlasmaHead()
        self.sheet    = SheetMetal()
        self.recorder = PathRecorder()

    # ------------------------------------------------------------------
    def update(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None:  # type: ignore[name-defined]
        """Advance the simulation by *dt* seconds based on held keys."""
        # --- Desired direction ---
        dx = dy = 0.0
        if keys[pygame.K_LEFT]:   dx -= 1.0
        if keys[pygame.K_RIGHT]:  dx += 1.0
        if keys[pygame.K_UP]:     dy -= 1.0
        if keys[pygame.K_DOWN]:   dy += 1.0

        # Normalise diagonal so speed stays constant in all directions
        if dx != 0.0 and dy != 0.0:
            dx *= 1.0 / math.sqrt(2.0)
            dy *= 1.0 / math.sqrt(2.0)

        # --- Speed modifier ---
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.head.set_speed(self._SPEED_BOOST)
        elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.head.set_speed(self._SPEED_PRECISION)
        else:
            self.head.set_speed(self._SPEED_NORMAL)

        # move() handles both acceleration and deceleration (dx=dy=0 → slow down)
        self.head.move(dx, dy, dt)

        # Cut the sheet whenever plasma is on and the head is physically moving
        if self.head.plasma_on and self.head.is_moving:
            self.sheet.cut(self.head.x, self.head.y)

        self.recorder.record(self.head.x, self.head.y, self.head.plasma_on)
