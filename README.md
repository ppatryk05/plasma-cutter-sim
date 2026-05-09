# 3D Printer Simulation (Task 6)

Python project for animated visualization of 3D printer operation, including:
- G-code parsing and timeline playback
- XYZ head kinematics with soft limits
- Thermal model for nozzle and bed
- Material deposition model (layered path reconstruction)
- Collision and safety checks
- Session replay (save/load)
- Desktop GUI with 3D viewport and diagnostics

## Quick start

1. Create a virtual environment and install dependencies:
   - `pip install -r requirements.txt`
2. Run:
   - `python -m src.main`

## Controls

- `Load G-code` to open a file
- `Play/Pause` to control simulation
- `Speed` slider for timeline speed
- `Export/Import Replay` to save and replay simulation runs

## Notes

- 3D viewport uses `pyqtgraph.opengl` to stay stable with PyQt6 integration.
- `ursina` is included in dependencies for optional future high-fidelity viewport mode.
