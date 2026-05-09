from __future__ import annotations

import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph.opengl.MeshData import MeshData

from src.core.types import PrinterConfig
from src.sim.simulator import SimulationFrame

# ---------------------------------------------------------------------------
# Color palette  — dark studio theme (high contrast, all parts clearly visible)
# ---------------------------------------------------------------------------
C_BG           = (0.96, 0.96, 0.97, 1.0)   # viewport background – clean white
C_BED_GLASS    = (0.07, 0.09, 0.14, 1.0)   # very dark navy glass plate
C_BED_FRAME    = (0.40, 0.42, 0.48, 1.0)   # aluminium bed frame – mid silver
C_BED_UNDER    = (0.30, 0.31, 0.36, 1.0)   # bed underside
C_GRID         = (0.30, 0.34, 0.50, 0.80)  # bright blue-gray grid on bed
C_FRAME_COL    = (0.28, 0.30, 0.35, 1.0)   # outer frame columns – dark steel
C_FRAME_BEAM   = (0.25, 0.27, 0.32, 1.0)   # outer frame beams – dark steel
C_BUILD_VOL    = (0.20, 0.50, 0.95, 0.50)  # blue build-volume wireframe
C_ROD          = (0.18, 0.18, 0.22, 1.0)   # gantry rods – dark charcoal (visible on white)
C_ROD_END      = (0.25, 0.25, 0.30, 1.0)   # rod end-connectors
C_BRACKET      = (0.30, 0.30, 0.35, 1.0)   # bracket arms
C_TOOLHEAD     = (0.93, 0.94, 0.96, 1.0)   # toolhead body – crisp white
C_FAN          = (0.06, 0.06, 0.09, 1.0)   # fan panel – near-black
C_HEATSINK     = (0.22, 0.24, 0.30, 1.0)   # heatsink – dark blue-steel
C_NOZZLE_BLK   = (0.82, 0.36, 0.04, 1.0)   # nozzle block – vivid copper/orange
C_NOZZLE_TIP   = (1.00, 0.72, 0.15, 1.0)   # nozzle tip – bright hot glow
C_FILAMENT     = (1.00, 0.45, 0.02, 1.0)   # extruded filament – vivid orange


# ---------------------------------------------------------------------------
# Mesh / geometry helpers
# ---------------------------------------------------------------------------

def _box_mesh(w: float, d: float, h: float) -> MeshData:
    """Solid box mesh centered at origin: w=X, d=Y, h=Z."""
    hw, hd, hh = w / 2, d / 2, h / 2
    v = np.array([
        [-hw,-hd,-hh],[ hw,-hd,-hh],[ hw, hd,-hh],[-hw, hd,-hh],
        [-hw,-hd, hh],[ hw,-hd, hh],[ hw, hd, hh],[-hw, hd, hh],
    ], dtype=float)
    f = np.array([
        [0,2,1],[0,3,2],[4,5,6],[4,6,7],
        [0,1,5],[0,5,4],[2,3,7],[2,7,6],
        [1,2,6],[1,6,5],[3,0,4],[3,4,7],
    ])
    return MeshData(vertexes=v, faces=f)


def _rect_mesh(x0, y0, z, x1, y1) -> MeshData:
    v = np.array([[x0,y0,z],[x1,y0,z],[x1,y1,z],[x0,y1,z]], dtype=float)
    return MeshData(vertexes=v, faces=np.array([[0,1,2],[0,2,3]]))


def _line_pairs(pairs: list) -> np.ndarray:
    out: list = []
    for a, b in pairs:
        out.append(a); out.append(b)
    return np.array(out, dtype=float)


def _mesh(w, d, h, color, edges=False, edge_color=(0,0,0,0.55)) -> gl.GLMeshItem:
    return gl.GLMeshItem(
        meshdata=_box_mesh(w, d, h), smooth=False, color=color,
        shader='shaded', drawEdges=edges, edgeColor=edge_color,
    )


def _flat(x0, y0, z, x1, y1, color) -> gl.GLMeshItem:
    return gl.GLMeshItem(
        meshdata=_rect_mesh(x0, y0, z, x1, y1), smooth=False,
        color=color, shader='shaded',
    )


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class Scene3DWidget(gl.GLViewWidget):
    """Realistic 3D printer 3D viewport with light background."""

    ROD_Y_OFFSET = 18.0
    ROD_Z_OFFSET = 63.0
    MARGIN       = 18.0
    COL_SIZE     = 14.0   # cross-section side of corner columns

    def __init__(self, config: PrinterConfig | None = None, parent=None) -> None:
        cfg = config or PrinterConfig()
        self.BX: float = cfg.build_x
        self.BY: float = cfg.build_y
        self.BZ: float = cfg.build_z
        self._dep_pts: list[list[float]] = []

        super().__init__(parent=parent)
        self.setBackgroundColor((210, 212, 218, 255))  # light gray viewport
        self.setCameraPosition(distance=660, elevation=24, azimuth=225)
        self.pan(self.BX / 2, self.BY / 2, 40)

        self._build_static()
        self._build_dynamic()
        self._update_moving_parts(0.0, 0.0, 0.0, extruding=False)

    # ------------------------------------------------------------------
    # Static geometry
    # ------------------------------------------------------------------
    def _build_static(self) -> None:
        bx, by, bz = self.BX, self.BY, self.BZ
        cx, cy = bx / 2, by / 2
        M      = self.MARGIN
        CS     = self.COL_SIZE
        BED_T  = 5.0
        POST_H = 45.0
        FLOOR_Z = -BED_T - POST_H             # z=0 of the floor
        COL_H  = bz + 40 - FLOOR_Z            # column spans from floor to top frame

        # --- Bed glass surface ---
        self.addItem(_flat(0, 0, 0, bx, by, C_BED_GLASS))

        # --- Bed aluminium frame border ---
        for x0, y0, x1, y1 in [
            (-M, -M, bx+M, 0), (-M, by, bx+M, by+M),
            (-M,  0, 0,    by), (bx,  0, bx+M, by),
        ]:
            self.addItem(_flat(x0, y0, -BED_T, x1, y1, C_BED_FRAME))
        self.addItem(_flat(-M, -M, -BED_T, bx+M, by+M, C_BED_UNDER))

        # --- Grid on bed surface ---
        bed_grid = gl.GLGridItem()
        bed_grid.scale(bx / 20, by / 20, 1)
        bed_grid.translate(cx, cy, 0.5)
        bed_grid.setColor(C_GRID)
        self.addItem(bed_grid)

        # --- Large floor grid (the surface the printer stands on) ---
        FLOOR_SIZE = 600.0   # total floor width/depth in mm
        floor_grid = gl.GLGridItem()
        floor_grid.scale(FLOOR_SIZE / 10, FLOOR_SIZE / 10, 1)
        floor_grid.translate(cx, cy, FLOOR_Z)
        floor_grid.setColor((0.45, 0.47, 0.52, 0.55))
        self.addItem(floor_grid)

        # Solid floor plane (subtle dark rectangle under the grid)
        self.addItem(_flat(
            cx - FLOOR_SIZE/2, cy - FLOOR_SIZE/2, FLOOR_Z - 0.5,
            cx + FLOOR_SIZE/2, cy + FLOOR_SIZE/2,
            (0.76, 0.77, 0.80, 1.0),
        ))

        # --- 4 corner columns (box mesh): span from floor to top frame ---
        for px, py in [(-M,-M),(bx+M,-M),(bx+M,by+M),(-M,by+M)]:
            col = _mesh(CS, CS, COL_H, C_FRAME_COL, edges=True, edge_color=(0,0,0,0.35))
            col.translate(px, py, FLOOR_Z + COL_H / 2)
            self.addItem(col)

        # --- Top frame beams (box mesh, solid rectangular section) ---
        top_z = bz + 40
        BEAM_H = 12.0
        BEAM_D = 12.0
        # front/back beams (along X)
        for ry in (-M, by+M):
            beam = _mesh(bx + 2*M + CS, BEAM_D, BEAM_H, C_FRAME_BEAM,
                         edges=True, edge_color=(0,0,0,0.30))
            beam.translate(cx, ry, top_z + BEAM_H/2)
            self.addItem(beam)
        # left/right beams (along Y)
        for rx in (-M, bx+M):
            beam = _mesh(BEAM_D, by + 2*M + CS, BEAM_H, C_FRAME_BEAM,
                         edges=True, edge_color=(0,0,0,0.30))
            beam.translate(rx, cy, top_z + BEAM_H/2)
            self.addItem(beam)

        # --- Build-volume wireframe ---
        c8 = [(0,0,0),(bx,0,0),(bx,by,0),(0,by,0),
              (0,0,bz),(bx,0,bz),(bx,by,bz),(0,by,bz)]
        ev  = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
               (0,4),(1,5),(2,6),(3,7)]
        self.addItem(gl.GLLinePlotItem(
            pos=_line_pairs([(c8[a], c8[b]) for a, b in ev]),
            color=C_BUILD_VOL, width=1.5, mode='lines', antialias=True,
        ))

    # ------------------------------------------------------------------
    # Dynamic geometry
    # ------------------------------------------------------------------
    def _build_dynamic(self) -> None:
        bx, M = self.BX, self.MARGIN

        rod_kw = dict(color=C_ROD, width=13, antialias=True)
        self._rod_f  = gl.GLLinePlotItem(pos=np.zeros((2,3)), **rod_kw)
        self._rod_b  = gl.GLLinePlotItem(pos=np.zeros((2,3)), **rod_kw)

        end_kw = dict(color=C_ROD_END, width=9, antialias=True)
        self._rod_el = gl.GLLinePlotItem(pos=np.zeros((2,3)), **end_kw)
        self._rod_er = gl.GLLinePlotItem(pos=np.zeros((2,3)), **end_kw)

        brk_kw = dict(color=C_BRACKET, width=6, antialias=True)
        self._brk_lf = gl.GLLinePlotItem(pos=np.zeros((2,3)), **brk_kw)
        self._brk_lb = gl.GLLinePlotItem(pos=np.zeros((2,3)), **brk_kw)
        self._brk_rf = gl.GLLinePlotItem(pos=np.zeros((2,3)), **brk_kw)
        self._brk_rb = gl.GLLinePlotItem(pos=np.zeros((2,3)), **brk_kw)

        # Toolhead – big near-white box with visible dark edges
        self._toolhead    = _mesh(52, 52, 54, C_TOOLHEAD,  edges=True, edge_color=(0,0,0,0.55))
        # Fan panel – dark recessed square
        self._fan_body    = _mesh(28,  4, 28, C_FAN)
        # Heatsink – dark block below toolhead with edge lines
        self._heatsink    = _mesh(20, 20, 22, C_HEATSINK,  edges=True, edge_color=(0,0,0,0.40))
        # Nozzle block – hot-copper colored
        self._nozzle_block= _mesh(11, 11, 13, C_NOZZLE_BLK)

        # Nozzle tip – bright glowing point (larger for visibility)
        self._nozzle_tip  = gl.GLScatterPlotItem(
            pos=np.array([[0.,0.,0.]]), size=15,
            color=C_NOZZLE_TIP, pxMode=True,
        )

        # Active filament strand (nozzle → bed, shown during extrusion)
        self._fil_strand  = gl.GLLinePlotItem(
            pos=np.zeros((2,3)), color=C_FILAMENT, width=4, antialias=True,
        )
        self._fil_strand.setVisible(False)

        # Accumulated deposition (thick, very visible)
        self._deposition  = gl.GLLinePlotItem(
            pos=np.empty((0,3)), color=C_FILAMENT, width=6,
            mode='lines', antialias=True,
        )

        for item in (
            self._rod_f, self._rod_b, self._rod_el, self._rod_er,
            self._brk_lf, self._brk_lb, self._brk_rf, self._brk_rb,
            self._toolhead, self._fan_body,
            self._heatsink, self._nozzle_block,
            self._nozzle_tip, self._fil_strand, self._deposition,
        ):
            self.addItem(item)

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------
    def _update_moving_parts(self, x: float, y: float, z: float, extruding: bool) -> None:
        bx, M = self.BX, self.MARGIN
        RY  = self.ROD_Y_OFFSET
        RZ  = z + self.ROD_Z_OFFSET
        yf  = y - RY
        yb  = y + RY

        # Gantry rods
        self._rod_f.setData(pos=np.array([[-M,yf,RZ],[bx+M,yf,RZ]], dtype=float))
        self._rod_b.setData(pos=np.array([[-M,yb,RZ],[bx+M,yb,RZ]], dtype=float))
        self._rod_el.setData(pos=np.array([[-M,yf,RZ],[-M,yb,RZ]], dtype=float))
        self._rod_er.setData(pos=np.array([[bx+M,yf,RZ],[bx+M,yb,RZ]], dtype=float))

        # Bracket arms (left x-25, right x+25, front/back rod)
        th_top = z + 64
        for ry, lattr, rattr in [(yf,'_brk_lf','_brk_rf'),(yb,'_brk_lb','_brk_rb')]:
            getattr(self,lattr).setData(pos=np.array([[x-26,ry,RZ],[x-26,ry,th_top]],dtype=float))
            getattr(self,rattr).setData(pos=np.array([[x+26,ry,RZ],[x+26,ry,th_top]],dtype=float))

        # Toolhead body centre at z+38
        th_cz = z + 38
        self._toolhead.resetTransform();     self._toolhead.translate(x, y, th_cz)
        self._fan_body.resetTransform();     self._fan_body.translate(x, y - 28, th_cz + 4)
        self._heatsink.resetTransform();     self._heatsink.translate(x, y, z + 15)
        self._nozzle_block.resetTransform(); self._nozzle_block.translate(x, y, z + 5.5)
        self._nozzle_tip.setData(pos=np.array([[x, y, z]]))

        if extruding and z > 0.05:
            self._fil_strand.setData(pos=np.array([[x,y,z],[x,y,0.0]],dtype=float))
            self._fil_strand.setVisible(True)
        else:
            self._fil_strand.setVisible(False)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def reset_scene(self) -> None:
        self._dep_pts = []
        self._deposition.setData(pos=np.empty((0,3)))
        self._update_moving_parts(0.0, 0.0, 0.0, extruding=False)

    def update_frame(self, previous: SimulationFrame | None, frame: SimulationFrame) -> None:
        sx, sy, sz = frame.state.x, frame.state.y, frame.state.z
        extruding = previous is not None and frame.state.e > previous.state.e
        self._update_moving_parts(sx, sy, sz, extruding=extruding)

        if extruding:
            self._dep_pts.extend([
                [previous.state.x, previous.state.y, previous.state.z],
                [sx, sy, sz],
            ])
            self._deposition.setData(pos=np.array(self._dep_pts))
