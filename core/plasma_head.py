class PlasmaHead:
    WORK_WIDTH = 1000  # mm
    WORK_HEIGHT = 600  # mm

    def __init__(self):
        self.x = self.WORK_WIDTH / 2.0
        self.y = self.WORK_HEIGHT / 2.0
        self.speed = 200.0  # mm/s
        self.plasma_on = False

    def move(self, dx: float, dy: float, dt: float) -> None:
        """Move head by (dx, dy) direction * speed * dt, clamped to working area."""
        self.x = max(0.0, min(self.WORK_WIDTH, self.x + dx * self.speed * dt))
        self.y = max(0.0, min(self.WORK_HEIGHT, self.y + dy * self.speed * dt))

    def toggle_plasma(self) -> None:
        """Toggle plasma on/off."""
        self.plasma_on = not self.plasma_on
