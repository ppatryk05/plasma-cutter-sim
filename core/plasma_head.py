import math


def _approach(current: float, target: float, step: float) -> float:
    """Move *current* toward *target* by at most *step* per call."""
    d = target - current
    if abs(d) <= step:
        return target
    return current + math.copysign(step, d)


class PlasmaHead:
    WORK_WIDTH  = 1000.0  # mm
    WORK_HEIGHT = 600.0   # mm

    # Keep the head centre at least this many mm from each edge so the
    # gantry carriage never visually exits the sheet boundary.
    # Derived from renderer constants (1 OpenGL unit = 100 mm):
    #   CARRIAGE_W = 0.30 OGL → 30 mm → half = 15 mm
    #   CARRIAGE_D = 0.34 OGL → 34 mm → half = 17 mm
    MARGIN_X = 15.0   # mm
    MARGIN_Y = 17.0   # mm

    ACCEL     = 600.0   # mm/s²  – acceleration / deceleration rate
    MIN_SPEED = 50.0    # mm/s
    MAX_SPEED = 500.0   # mm/s

    def __init__(self) -> None:
        self.x:         float = self.WORK_WIDTH  / 2.0
        self.y:         float = self.WORK_HEIGHT / 2.0
        self.speed:     float = 200.0   # target travel speed mm/s
        self.plasma_on: bool  = False
        self._vx:       float = 0.0     # current velocity X mm/s
        self._vy:       float = 0.0     # current velocity Y mm/s

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def current_speed(self) -> float:
        """Actual movement speed magnitude in mm/s."""
        return math.sqrt(self._vx ** 2 + self._vy ** 2)

    @property
    def is_moving(self) -> bool:
        """True when the head is moving fast enough to leave a cut mark."""
        return self.current_speed > 0.5

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------
    def move(self, dx: float, dy: float, dt: float) -> None:
        """Accelerate toward direction (dx, dy) then advance position.

        Pass dx=dy=0 when no input is active to trigger smooth deceleration.
        dx, dy are expected to be unit-length (diagonal already normalised).
        Clamps position so the gantry body stays within the sheet boundary.
        """
        step = self.ACCEL * dt
        self._vx = _approach(self._vx, dx * self.speed, step)
        self._vy = _approach(self._vy, dy * self.speed, step)

        new_x = self.x + self._vx * dt
        new_y = self.y + self._vy * dt

        clamped_x = max(self.MARGIN_X,
                        min(self.WORK_WIDTH  - self.MARGIN_X, new_x))
        clamped_y = max(self.MARGIN_Y,
                        min(self.WORK_HEIGHT - self.MARGIN_Y, new_y))

        # Kill the velocity component that hit a wall
        if clamped_x != new_x:
            self._vx = 0.0
        if clamped_y != new_y:
            self._vy = 0.0

        self.x = clamped_x
        self.y = clamped_y

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------
    def toggle_plasma(self) -> None:
        """Toggle plasma on/off."""
        self.plasma_on = not self.plasma_on

    def set_speed(self, speed: float) -> None:
        """Set target travel speed, clamped to [MIN_SPEED, MAX_SPEED]."""
        self.speed = max(self.MIN_SPEED, min(self.MAX_SPEED, speed))

    def reset(self) -> None:
        """Return head to centre, stop all motion, and turn plasma off."""
        self.x = self.WORK_WIDTH  / 2.0
        self.y = self.WORK_HEIGHT / 2.0
        self._vx = 0.0
        self._vy = 0.0
        self.plasma_on = False
