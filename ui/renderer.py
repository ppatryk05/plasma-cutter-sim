import pygame
import math
import random

from core.plasma_head import PlasmaHead
from core.sheet_metal import SheetMetal


class Renderer:
    WINDOW_W = 1280
    WINDOW_H = 720

    # Colours
    BG_COLOR = (25, 25, 25)
    FRAME_COLOR = (60, 60, 60)
    BEAM_COLOR = (90, 90, 100)
    CARRIAGE_COLOR = (110, 110, 120)
    HEAD_COLOR = (200, 200, 210)
    RAIL_COLOR = (70, 70, 80)
    PLASMA_OUTER = (255, 180, 0, 120)
    PLASMA_INNER = (255, 255, 180, 200)

    # Layout margins around the working area
    MARGIN = 60

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_W, self.WINDOW_H))
        pygame.display.set_caption("Plasma Cutter Simulator")
        self.font = pygame.font.SysFont("consolas", 16)
        self.font_big = pygame.font.SysFont("consolas", 20, bold=True)

        # Compute scale so working area fits inside the window with margins
        avail_w = self.WINDOW_W - 2 * self.MARGIN
        avail_h = self.WINDOW_H - 2 * self.MARGIN
        scale_x = avail_w / PlasmaHead.WORK_WIDTH
        scale_y = avail_h / PlasmaHead.WORK_HEIGHT
        self.scale = min(scale_x, scale_y)

        # Top-left corner of the working area on screen
        wa_w = int(PlasmaHead.WORK_WIDTH * self.scale)
        wa_h = int(PlasmaHead.WORK_HEIGHT * self.scale)
        self.wa_x = (self.WINDOW_W - wa_w) // 2
        self.wa_y = (self.WINDOW_H - wa_h) // 2
        self.wa_w = wa_w
        self.wa_h = wa_h

        # Spark state
        self._sparks: list[dict] = []

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------
    def _mm_to_screen(self, x_mm: float, y_mm: float) -> tuple[int, int]:
        sx = self.wa_x + int(x_mm * self.scale)
        sy = self.wa_y + int(y_mm * self.scale)
        return sx, sy

    # ------------------------------------------------------------------
    # Spark / glow helpers
    # ------------------------------------------------------------------
    def _update_sparks(self, head: PlasmaHead, dt: float) -> None:
        if head.plasma_on:
            for _ in range(6):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(30, 120)
                self._sparks.append({
                    "x": float(head.x),
                    "y": float(head.y),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": random.uniform(0.15, 0.4),
                    "age": 0.0,
                })
        for s in self._sparks:
            s["age"] += dt
            s["x"] += s["vx"] * dt
            s["y"] += s["vy"] * dt
        self._sparks = [s for s in self._sparks if s["age"] < s["life"]]

    def _draw_glow(self, sx: int, sy: int) -> None:
        """Draw a soft glow / spark effect around the head."""
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for radius, alpha in [(50, 30), (35, 60), (20, 100), (10, 180)]:
            color = (255, 200, 50, alpha)
            pygame.draw.circle(glow_surf, color, (60, 60), radius)
        self.screen.blit(glow_surf, (sx - 60, sy - 60))

        # Sparks (converted from mm offsets to screen coords)
        for s in self._sparks:
            frac = s["age"] / s["life"]
            alpha = int(255 * (1 - frac))
            r = max(1, int(3 * (1 - frac)))
            spx, spy = self._mm_to_screen(s["x"], s["y"])
            spark_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(spark_surf, (255, 240, 100, alpha), (r + 1, r + 1), r)
            self.screen.blit(spark_surf, (spx - r - 1, spy - r - 1))

    # ------------------------------------------------------------------
    # Main draw
    # ------------------------------------------------------------------
    def draw(self, head: PlasmaHead, sheet: SheetMetal, dt: float = 0.016) -> None:
        self._update_sparks(head, dt)

        # --- Background ---
        self.screen.fill(self.BG_COLOR)

        # --- Sheet metal surface ---
        sheet_surf = sheet.get_surface(self.scale)
        self.screen.blit(sheet_surf, (self.wa_x, self.wa_y))

        # --- Working area border ---
        pygame.draw.rect(
            self.screen, self.FRAME_COLOR,
            (self.wa_x, self.wa_y, self.wa_w, self.wa_h), 2
        )

        # --- Machine rails (outer frame) ---
        rail_thickness = 12
        # Top rail
        pygame.draw.rect(
            self.screen, self.RAIL_COLOR,
            (self.wa_x - 20, self.wa_y - rail_thickness, self.wa_w + 40, rail_thickness)
        )
        # Bottom rail
        pygame.draw.rect(
            self.screen, self.RAIL_COLOR,
            (self.wa_x - 20, self.wa_y + self.wa_h, self.wa_w + 40, rail_thickness)
        )

        # --- Horizontal beam (follows Y of head) ---
        head_sx, head_sy = self._mm_to_screen(head.x, head.y)
        beam_h = 14
        pygame.draw.rect(
            self.screen, self.BEAM_COLOR,
            (self.wa_x - 20, head_sy - beam_h // 2, self.wa_w + 40, beam_h)
        )
        # Beam highlight line
        pygame.draw.rect(
            self.screen, (130, 130, 145),
            (self.wa_x - 20, head_sy - beam_h // 2 + 2, self.wa_w + 40, 3)
        )

        # --- Vertical carriage (follows X of head) on the beam ---
        carriage_w = 18
        carriage_h = 30
        pygame.draw.rect(
            self.screen, self.CARRIAGE_COLOR,
            (head_sx - carriage_w // 2, head_sy - carriage_h // 2,
             carriage_w, carriage_h)
        )

        # --- Plasma head (small circle) ---
        head_radius = 6
        pygame.draw.circle(self.screen, self.HEAD_COLOR, (head_sx, head_sy), head_radius)
        pygame.draw.circle(self.screen, (50, 50, 55), (head_sx, head_sy), head_radius, 2)

        # --- Plasma glow / sparks when ON ---
        if head.plasma_on:
            self._draw_glow(head_sx, head_sy)
            # Re-draw head on top of glow
            pygame.draw.circle(self.screen, (255, 255, 200), (head_sx, head_sy), head_radius)
            pygame.draw.circle(self.screen, (200, 180, 0), (head_sx, head_sy), head_radius, 2)

        # --- HUD ---
        self._draw_hud(head)

        pygame.display.flip()

    def _draw_hud(self, head: PlasmaHead) -> None:
        plasma_str = "ON " if head.plasma_on else "OFF"
        plasma_color = (255, 220, 50) if head.plasma_on else (160, 160, 160)

        lines = [
            (f"X: {head.x:7.1f} mm", (220, 220, 220)),
            (f"Y: {head.y:7.1f} mm", (220, 220, 220)),
            (f"Speed: {head.speed:.0f} mm/s", (180, 180, 180)),
        ]
        hud_x, hud_y = 10, 10
        for text, color in lines:
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (hud_x, hud_y))
            hud_y += 22

        plasma_label = self.font_big.render(f"PLASMA: {plasma_str}", True, plasma_color)
        self.screen.blit(plasma_label, (hud_x, hud_y))
