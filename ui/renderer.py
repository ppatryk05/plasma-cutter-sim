"""3D OpenGL renderer for the Plasma Cutter Simulator.

Coordinate system
-----------------
  1 OpenGL unit = 100 mm
  Working area: 1000 mm × 600 mm  →  10.0 × 6.0 OpenGL units
  Sheet metal lies in the XZ plane at Y = 0.
  head.x (0–1000 mm) maps to X (0–10).
  head.y (0–600  mm) maps to Z (0–6).
  Y is the vertical (up) axis.
"""

import math
import random

import numpy as np
import pygame
from OpenGL.GL import *   # noqa: F401,F403
from OpenGL.GLU import *  # noqa: F401,F403

from core.plasma_head import PlasmaHead
from core.sheet_metal import SheetMetal

# ---------------------------------------------------------------------------
# Scene constants
# ---------------------------------------------------------------------------
MM_TO_GL = 1.0 / 100.0          # multiply mm by this to get OpenGL units

SHEET_X0, SHEET_X1 = 0.0, 10.0  # sheet X bounds
SHEET_Z0, SHEET_Z1 = 0.0, 6.0   # sheet Z bounds
SHEET_Y = 0.0                    # Y level of the sheet top surface

# Gantry geometry (all in OpenGL units)
RAIL_H         = 0.20   # height of side rails above sheet
RAIL_THICKNESS = 0.18   # rail depth (Z direction)
RAIL_EXT       = 0.22   # rail extension beyond sheet in X

BEAM_H = 0.24           # beam cross-section height
BEAM_D = 0.20           # beam cross-section depth

CARRIAGE_W = 0.30       # width along X
CARRIAGE_D = 0.34       # depth along Z
CARRIAGE_H = 0.40       # height along Y

HEAD_W = 0.18           # plasma-head box
HEAD_D = 0.18
HEAD_H = 0.28

NOZZLE_R = 0.055        # nozzle half-size


class Renderer:
    WINDOW_W = 1280
    WINDOW_H = 720

    # Resolution of the sheet-metal texture (power-of-two friendly)
    TEX_W = 512
    TEX_H = 256

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.WINDOW_W, self.WINDOW_H),
            pygame.OPENGL | pygame.DOUBLEBUF,
        )
        pygame.display.set_caption("Plasma Cutter Simulator 3D")
        self.font     = pygame.font.SysFont("consolas", 18)
        self.font_big = pygame.font.SysFont("consolas", 22, bold=True)

        # --- Camera (spherical coords around a fixed target) ---
        self.cam_azimuth   = 30.0   # degrees, horizontal
        self.cam_elevation = 42.0   # degrees, vertical
        self.cam_distance  = 13.0   # OpenGL units
        self.cam_target    = [5.0, 0.0, 3.0]  # centre of the sheet

        self._mouse_dragging = False
        self._mouse_last: tuple[int, int] = (0, 0)

        # --- 3-D spark particles ---
        self._sparks: list[dict] = []

        # --- Sheet-metal texture ---
        self._sheet_tex: int | None = None
        self._sheet_tex_version: int = -1   # last SheetMetal.version we uploaded

        # --- HUD text texture cache: slot index → (tex_id, w, h, last_text, last_color) ---
        # One fixed slot per HUD line; texture is re-created only when text/color changes.
        self._hud_slots: list[tuple | None] = [None, None, None, None]

        self._init_gl()

    # ------------------------------------------------------------------
    # OpenGL initialisation
    # ------------------------------------------------------------------
    def _init_gl(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.08, 0.08, 0.10, 1.0)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        # Allocate the sheet texture handle
        self._sheet_tex = int(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self._sheet_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)

        self._set_projection()

    def _set_projection(self) -> None:
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, self.WINDOW_W / self.WINDOW_H, 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)

    def _apply_camera(self) -> None:
        glLoadIdentity()
        az = math.radians(self.cam_azimuth)
        el = math.radians(self.cam_elevation)
        cx = self.cam_target[0] + self.cam_distance * math.cos(el) * math.sin(az)
        cy = self.cam_target[1] + self.cam_distance * math.sin(el)
        cz = self.cam_target[2] + self.cam_distance * math.cos(el) * math.cos(az)
        gluLookAt(cx, cy, cz,
                  self.cam_target[0], self.cam_target[1], self.cam_target[2],
                  0.0, 1.0, 0.0)

    # ------------------------------------------------------------------
    # Camera / mouse event handling
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        """Process mouse events for camera orbit and zoom."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._mouse_dragging = True
            self._mouse_last = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._mouse_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self._mouse_dragging:
                dx = event.pos[0] - self._mouse_last[0]
                dy = event.pos[1] - self._mouse_last[1]
                self.cam_azimuth   = (self.cam_azimuth - dx * 0.4) % 360.0
                self.cam_elevation = max(5.0, min(85.0, self.cam_elevation - dy * 0.4))
                self._mouse_last = event.pos
        elif event.type == pygame.MOUSEWHEEL:
            self.cam_distance = max(2.0, min(30.0, self.cam_distance - event.y * 0.6))

    # ------------------------------------------------------------------
    # Sheet-metal texture
    # ------------------------------------------------------------------
    def _upload_sheet_texture(self, sheet: SheetMetal) -> None:
        """Build an RGB texture from the sheet grid and upload to GPU."""
        ix = np.round(np.linspace(0, sheet.width  - 1, self.TEX_W)).astype(int)
        iy = np.round(np.linspace(0, sheet.height - 1, self.TEX_H)).astype(int)
        sub = sheet.grid[np.ix_(iy, ix)]          # (TEX_H, TEX_W) bool

        img = np.empty((self.TEX_H, self.TEX_W, 3), dtype=np.uint8)
        img[ sub] = (22,  15,  10)    # cut areas  – very dark
        img[~sub] = (145, 140, 130)   # intact     – grey metal

        glBindTexture(GL_TEXTURE_2D, self._sheet_tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                     self.TEX_W, self.TEX_H, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, img.tobytes())
        glBindTexture(GL_TEXTURE_2D, 0)

    # ------------------------------------------------------------------
    # Drawing primitives
    # ------------------------------------------------------------------
    def _draw_box(self,
                  x0: float, y0: float, z0: float,
                  x1: float, y1: float, z1: float,
                  color: tuple) -> None:
        """Draw a solid axis-aligned box with a flat colour."""
        glColor3f(*color)
        glBegin(GL_QUADS)
        # Top (+Y)
        glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0)
        glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
        # Bottom (−Y)
        glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1)
        glVertex3f(x1, y0, z0); glVertex3f(x0, y0, z0)
        # Front (+Z)
        glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1)
        glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
        # Back (−Z)
        glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0)
        glVertex3f(x1, y0, z0); glVertex3f(x0, y0, z0)
        # Right (+X)
        glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1)
        glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)
        # Left (−X)
        glVertex3f(x0, y1, z0); glVertex3f(x0, y1, z1)
        glVertex3f(x0, y0, z1); glVertex3f(x0, y0, z0)
        glEnd()

    # ------------------------------------------------------------------
    # Scene elements
    # ------------------------------------------------------------------
    def _draw_sheet(self, sheet: SheetMetal) -> None:
        # Thin slab for the sheet body
        self._draw_box(SHEET_X0, -0.06, SHEET_Z0,
                       SHEET_X1, SHEET_Y, SHEET_Z1,
                       (0.22, 0.20, 0.18))

        # Only rebuild the GPU texture when the grid has been modified
        if sheet.version != self._sheet_tex_version:
            self._upload_sheet_texture(sheet)
            self._sheet_tex_version = sheet.version
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self._sheet_tex)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        # texCoord (s, t=0) → first uploaded row → grid row 0 → sim y=0 → Z=0 (near)
        # texCoord (s, t=1) → last  uploaded row → grid row N → sim y=600 → Z=6 (far)
        glTexCoord2f(0.0, 0.0); glVertex3f(SHEET_X0, SHEET_Y, SHEET_Z0)
        glTexCoord2f(1.0, 0.0); glVertex3f(SHEET_X1, SHEET_Y, SHEET_Z0)
        glTexCoord2f(1.0, 1.0); glVertex3f(SHEET_X1, SHEET_Y, SHEET_Z1)
        glTexCoord2f(0.0, 1.0); glVertex3f(SHEET_X0, SHEET_Y, SHEET_Z1)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    def _draw_gantry(self, head: PlasmaHead) -> None:
        hx = head.x * MM_TO_GL   # 0 … 10
        hz = head.y * MM_TO_GL   # 0 … 6

        c_rail     = (0.32, 0.32, 0.38)
        c_leg      = (0.25, 0.25, 0.30)
        c_beam     = (0.38, 0.38, 0.46)
        c_carriage = (0.50, 0.50, 0.60)
        c_head     = (0.68, 0.68, 0.78)
        c_nozzle   = (0.82, 0.82, 0.90)

        rail_y0 = SHEET_Y
        rail_y1 = SHEET_Y + RAIL_H

        # --- Two side rails along X ---
        for zr0, zr1 in (
            (SHEET_Z0 - RAIL_THICKNESS, SHEET_Z0),
            (SHEET_Z1, SHEET_Z1 + RAIL_THICKNESS),
        ):
            self._draw_box(SHEET_X0 - RAIL_EXT, rail_y0, zr0,
                           SHEET_X1 + RAIL_EXT, rail_y1, zr1, c_rail)

        # --- End-legs at each corner ---
        z_leg0 = SHEET_Z0 - RAIL_THICKNESS
        z_leg1 = SHEET_Z1 + RAIL_THICKNESS
        for ex in (SHEET_X0 - RAIL_EXT, SHEET_X1 + RAIL_EXT - 0.12):
            self._draw_box(ex, -0.40, z_leg0,
                           ex + 0.12, rail_y0, z_leg1, c_leg)

        # --- Horizontal beam spanning X, following Z = head.y ---
        beam_y0 = rail_y1
        beam_y1 = beam_y0 + BEAM_H
        self._draw_box(SHEET_X0 - RAIL_EXT, beam_y0, hz - BEAM_D * 0.5,
                       SHEET_X1 + RAIL_EXT, beam_y1, hz + BEAM_D * 0.5, c_beam)

        # --- Carriage on beam, following X = head.x ---
        car_y0 = beam_y0 - 0.04
        car_y1 = beam_y1 + 0.06
        self._draw_box(hx - CARRIAGE_W * 0.5, car_y0, hz - CARRIAGE_D * 0.5,
                       hx + CARRIAGE_W * 0.5, car_y1, hz + CARRIAGE_D * 0.5,
                       c_carriage)

        # --- Plasma-head body hanging from carriage ---
        hd_y1 = car_y0
        hd_y0 = hd_y1 - HEAD_H
        self._draw_box(hx - HEAD_W * 0.5, hd_y0, hz - HEAD_D * 0.5,
                       hx + HEAD_W * 0.5, hd_y1, hz + HEAD_D * 0.5, c_head)

        # --- Nozzle tip ---
        nz_y1 = hd_y0
        nz_y0 = nz_y1 - 0.17
        self._draw_box(hx - NOZZLE_R, nz_y0, hz - NOZZLE_R,
                       hx + NOZZLE_R, nz_y1, hz + NOZZLE_R, c_nozzle)

    def _draw_plasma_glow(self, head: PlasmaHead) -> None:
        hx = head.x * MM_TO_GL
        hz = head.y * MM_TO_GL
        y_glow = SHEET_Y + 0.01

        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)   # additive for glow

        layers = [
            (0.42, (1.0, 0.45, 0.00, 0.12)),
            (0.30, (1.0, 0.60, 0.00, 0.22)),
            (0.18, (1.0, 0.80, 0.10, 0.42)),
            (0.10, (1.0, 0.95, 0.40, 0.66)),
            (0.05, (1.0, 1.00, 0.90, 0.90)),
        ]
        for size, color in layers:
            glColor4f(*color)
            glBegin(GL_QUADS)
            glVertex3f(hx - size, y_glow, hz - size)
            glVertex3f(hx + size, y_glow, hz - size)
            glVertex3f(hx + size, y_glow, hz + size)
            glVertex3f(hx - size, y_glow, hz + size)
            glEnd()

        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # ------------------------------------------------------------------
    # Sparks
    # ------------------------------------------------------------------
    def _update_sparks(self, head: PlasmaHead, dt: float) -> None:
        if head.plasma_on:
            hx = head.x * MM_TO_GL
            hz = head.y * MM_TO_GL
            for _ in range(5):
                angle_h = random.uniform(0.0, 2 * math.pi)
                speed_h = random.uniform(0.8, 3.0)
                speed_v = random.uniform(0.5, 2.0)
                self._sparks.append({
                    "x": hx, "y": SHEET_Y + 0.05, "z": hz,
                    "vx": math.cos(angle_h) * speed_h,
                    "vy": speed_v,
                    "vz": math.sin(angle_h) * speed_h,
                    "life": random.uniform(0.15, 0.55),
                    "age":  0.0,
                })
        for s in self._sparks:
            s["age"] += dt
            s["x"]   += s["vx"] * dt
            s["y"]   += s["vy"] * dt
            s["z"]   += s["vz"] * dt
            s["vy"]  -= 5.0 * dt      # gravity
        self._sparks = [s for s in self._sparks if s["age"] < s["life"]]

    def _draw_sparks(self) -> None:
        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glPointSize(3.5)
        glBegin(GL_POINTS)
        for s in self._sparks:
            frac  = s["age"] / s["life"]
            alpha = 1.0 - frac
            glColor4f(1.0, max(0.0, 0.9 - frac * 0.6), 0.0, alpha)
            glVertex3f(s["x"], s["y"], s["z"])
        glEnd()
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # ------------------------------------------------------------------
    # 2-D HUD overlay
    # ------------------------------------------------------------------
    def _draw_hud(self, head: PlasmaHead) -> None:
        """Switch to orthographic 2-D projection and draw the status HUD."""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0.0, self.WINDOW_W, self.WINDOW_H, 0.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        plasma_str   = "ON " if head.plasma_on else "OFF"
        plasma_color = (255, 220, 50) if head.plasma_on else (160, 160, 160)

        lines = [
            (f"X: {head.x:7.1f} mm",           (220, 220, 220), self.font),
            (f"Y: {head.y:7.1f} mm",           (220, 220, 220), self.font),
            (f"Speed: {head.speed:.0f} mm/s",  (180, 180, 180), self.font),
            (f"PLASMA: {plasma_str}",           plasma_color,    self.font_big),
        ]

        hud_x, hud_y = 12, 12
        for slot, (text, color, fnt) in enumerate(lines):
            self._blit_text(slot, text, fnt, color, hud_x, hud_y)
            hud_y += fnt.get_linesize() + 4

        # Restore 3-D state
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)

    def _blit_text(self,
                   slot:  int,
                   text:  str,
                   font:  pygame.font.Font,
                   color: tuple,
                   x:     int,
                   y:     int) -> None:
        """Render a pygame font surface as an OpenGL textured quad.

        Each HUD line uses a fixed *slot* (0–3).  The GPU texture is only
        re-created when the text or colour actually changes, keeping GPU
        allocations to a minimum.
        """
        cached = self._hud_slots[slot]
        if cached is None or cached[3] != text or cached[4] != color:
            # Release the old texture for this slot if any
            if cached is not None:
                glDeleteTextures(cached[0])

            surf = font.render(text, True, color)
            w, h = surf.get_size()
            # flip=False: row 0 of data == pygame row 0 (top) == OpenGL t=0 (bottom).
            # With glOrtho(0,W,H,0) and texcoords mapped consistently this renders upright.
            data = pygame.image.tostring(surf, "RGBA", False)

            tex_id = int(glGenTextures(1))
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, data)
            glBindTexture(GL_TEXTURE_2D, 0)
            self._hud_slots[slot] = (tex_id, w, h, text, color)
            cached = self._hud_slots[slot]

        tex_id, w, h, _text, _color = cached
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex2f(x,     y)
        glTexCoord2f(1.0, 0.0); glVertex2f(x + w, y)
        glTexCoord2f(1.0, 1.0); glVertex2f(x + w, y + h)
        glTexCoord2f(0.0, 1.0); glVertex2f(x,     y + h)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    # ------------------------------------------------------------------
    # Main draw call
    # ------------------------------------------------------------------
    def draw(self, head: PlasmaHead, sheet: SheetMetal, dt: float = 0.016) -> None:
        self._update_sparks(head, dt)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        self._apply_camera()

        self._draw_sheet(sheet)
        self._draw_gantry(head)

        if head.plasma_on:
            self._draw_plasma_glow(head)

        if self._sparks:
            self._draw_sparks()

        self._draw_hud(head)

        pygame.display.flip()

