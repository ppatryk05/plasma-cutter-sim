import sys

import pygame

from core.machine import CutterMachine
from ui.renderer import Renderer


def main() -> None:
    machine  = CutterMachine()
    renderer = Renderer()

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # seconds

        # --- Events ---
        for event in pygame.event.get():
            renderer.handle_event(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    machine.head.toggle_plasma()
                elif event.key == pygame.K_r:
                    machine.head.reset()
                elif event.key == pygame.K_c:
                    machine.sheet.clear()
                elif event.key == pygame.K_RIGHTBRACKET:
                    machine.head.set_speed(machine.head.speed + 50.0)
                elif event.key == pygame.K_LEFTBRACKET:
                    machine.head.set_speed(machine.head.speed - 50.0)

        # --- Simulation step ---
        keys = pygame.key.get_pressed()
        machine.update(keys, dt)

        # --- Draw ---
        renderer.draw(machine.head, machine.sheet, dt)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
