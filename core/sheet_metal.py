import numpy as np
import pygame


class SheetMetal:
    def __init__(self):
        self.width = 1000   # mm / pixels in the grid
        self.height = 600   # mm / pixels in the grid
        # False = intact sheet, True = cut away
        self.grid = np.zeros((self.height, self.width), dtype=bool)

    def cut(self, x: float, y: float, radius: int = 3) -> None:
        """Mark a circular area around (x, y) as cut."""
        cx = int(round(x))
        cy = int(round(y))
        x0 = max(0, cx - radius)
        x1 = min(self.width, cx + radius + 1)
        y0 = max(0, cy - radius)
        y1 = min(self.height, cy + radius + 1)

        xs = np.arange(x0, x1)
        ys = np.arange(y0, y1)
        xx, yy = np.meshgrid(xs, ys)
        mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2
        self.grid[y0:y1, x0:x1][mask] = True

    def get_surface(self, scale: float) -> pygame.Surface:
        """Return a pygame.Surface showing the sheet at the given scale.

        Args:
            scale: pixels per mm
        Returns:
            pygame.Surface (RGB)
        """
        w = int(self.width * scale)
        h = int(self.height * scale)

        # Build small numpy RGB image then scale up
        # intact = grey (160,160,160), cut = black (0,0,0)
        channel = np.where(self.grid, 0, 160).astype(np.uint8)
        img = np.stack([channel, channel, channel], axis=2)

        surface_small = pygame.surfarray.make_surface(
            np.transpose(img, (1, 0, 2))  # pygame expects (x, y, channels)
        )
        if abs(scale - 1.0) < 1e-6:
            return surface_small
        return pygame.transform.scale(surface_small, (w, h))
