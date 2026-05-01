import math
import sys
import pygame

from core.plasma_head import PlasmaHead
from core.sheet_metal import SheetMetal
from ui.renderer import Renderer


def main() -> None:
    head = PlasmaHead()
    sheet = SheetMetal()
    renderer = Renderer()

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # seconds

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    head.toggle_plasma()

        # --- Movement ---
        keys = pygame.key.get_pressed()
        dx = dy = 0.0
        if keys[pygame.K_LEFT]:
            dx = -1.0
        if keys[pygame.K_RIGHT]:
            dx = 1.0
        if keys[pygame.K_UP]:
            dy = -1.0
        if keys[pygame.K_DOWN]:
            dy = 1.0

        if dx != 0.0 or dy != 0.0:
            # Normalise diagonal movement
            if dx != 0.0 and dy != 0.0:
                factor = 1 / math.sqrt(2)
                dx *= factor
                dy *= factor
            head.move(dx, dy, dt)

            # Cut when plasma is on and head is moving
            if head.plasma_on:
                sheet.cut(head.x, head.y)

        # --- Draw ---
        renderer.draw(head, sheet, dt)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
