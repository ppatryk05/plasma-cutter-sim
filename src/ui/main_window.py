from __future__ import annotations

from pathlib import Path

import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.core.gcode_parser import parse_gcode_file
from src.core.types import PrinterConfig
from src.io.session_replay import export_frames
from src.render.scene3d import Scene3DWidget
from src.sim.simulator import PrinterSimulator, SimulationFrame


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("3D Printer Simulator")
        self.resize(1400, 900)

        self.config = PrinterConfig()
        self.sim = PrinterSimulator(self.config)
        self.frames: list[SimulationFrame] = []
        self.frame_idx = 0
        self.playing = False
        self.last_file = Path("examples/sample.gcode")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)

        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)

        self.scene = Scene3DWidget(config=self.config)
        layout.addWidget(self.scene, stretch=3)

        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        layout.addWidget(sidebar, stretch=2)

        self.status_label = QLabel("Załaduj plik G-code aby zacząć")
        self.status_label.setWordWrap(True)
        sidebar_layout.addWidget(self.status_label)

        load_btn = QPushButton("Załaduj G-code")
        load_btn.clicked.connect(self.load_gcode)
        sidebar_layout.addWidget(load_btn)

        play_btn = QPushButton("Play / Pauza  [Spacja]")
        play_btn.clicked.connect(self.toggle_play)
        sidebar_layout.addWidget(play_btn)

        restart_btn = QPushButton("Restart")
        restart_btn.clicked.connect(self.restart)
        sidebar_layout.addWidget(restart_btn)

        export_btn = QPushButton("Zapisz sesję (JSON)")
        export_btn.clicked.connect(self.export_replay)
        sidebar_layout.addWidget(export_btn)

        self._speed_label = QLabel("Prędkość: 5×")
        sidebar_layout.addWidget(self._speed_label)
        self.speed = QSlider()
        self.speed.setOrientation(Qt.Orientation.Horizontal)
        self.speed.setRange(1, 50)
        self.speed.setValue(5)
        self.speed.valueChanged.connect(
            lambda v: self._speed_label.setText(f"Prędkość: {v}×")
        )
        sidebar_layout.addWidget(self.speed)

        sidebar_layout.addWidget(QLabel("Temperatura [°C]:"))
        self.temp_plot = pg.PlotWidget()
        self.temp_plot.setMaximumHeight(200)
        self.temp_plot.addLegend()
        self.temp_plot.setLabel("left", "°C")
        self.nozzle_curve = self.temp_plot.plot([], [], pen=pg.mkPen("r", width=2), name="Dysza")
        self.bed_curve = self.temp_plot.plot([], [], pen=pg.mkPen("y", width=2), name="Stół")
        sidebar_layout.addWidget(self.temp_plot)

        sidebar_layout.addWidget(QLabel("Ekstruzja (E):"))
        self.progress_plot = pg.PlotWidget()
        self.progress_plot.setMaximumHeight(160)
        self.progress_plot.setLabel("left", "mm")
        self.extrusion_curve = self.progress_plot.plot([], [], pen=pg.mkPen("c", width=2))
        sidebar_layout.addWidget(self.progress_plot)

        sidebar_layout.addStretch(1)

        if self.last_file.exists():
            self._load_from_path(self.last_file)

    # ------------------------------------------------------------------
    def _load_from_path(self, path: Path) -> None:
        commands = parse_gcode_file(path)
        self.frames = self.sim.run(commands)
        self.frame_idx = 0
        self.playing = False
        self.scene.reset_scene()
        self._refresh_charts()
        self.status_label.setText(f"Załadowano: {path.name}  ({len(self.frames)} kroków)")

    def load_gcode(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "Otwórz G-code", str(self.last_file.parent),
            "G-code (*.gcode *.gc *.txt);;Wszystkie pliki (*)",
        )
        if filename:
            self.last_file = Path(filename)
            self._load_from_path(self.last_file)

    def toggle_play(self) -> None:
        if not self.frames:
            self.status_label.setText("Brak danych – załaduj G-code")
            return
        self.playing = not self.playing

    def restart(self) -> None:
        self.frame_idx = 0
        self.playing = False
        self.scene.reset_scene()
        self.status_label.setText("Restart – naciśnij Play aby zacząć od nowa")

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() == Qt.Key.Key_Space:
            self.toggle_play()
        else:
            super().keyPressEvent(event)

    def _tick(self) -> None:
        if not self.playing or not self.frames:
            return
        steps = self.speed.value()
        for _ in range(steps):
            if self.frame_idx >= len(self.frames):
                self.playing = False
                self.status_label.setText("Druk zakończony")
                break
            previous = self.frames[self.frame_idx - 1] if self.frame_idx > 0 else None
            frame = self.frames[self.frame_idx]
            self.scene.update_frame(previous, frame)

            s = frame.state
            info = (
                f"t={s.t:.1f}s  "
                f"X={s.x:.1f}  Y={s.y:.1f}  Z={s.z:.2f}  "
                f"E={s.e:.2f}  "
                f"Dysza={s.nozzle_temp:.0f}°C  Stół={s.bed_temp:.0f}°C"
            )
            if frame.issues:
                info = "⚠ " + " | ".join(frame.issues) + "  |  " + info
            self.status_label.setText(info)
            self.frame_idx += 1

    def _refresh_charts(self) -> None:
        t = [f.state.t for f in self.frames]
        self.nozzle_curve.setData(t, [f.state.nozzle_temp for f in self.frames])
        self.bed_curve.setData(t, [f.state.bed_temp for f in self.frames])
        self.extrusion_curve.setData(t, [f.state.e for f in self.frames])

    def export_replay(self) -> None:
        if not self.frames:
            self.status_label.setText("Brak danych do zapisania")
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Zapisz sesję", "sesja.json", "JSON (*.json)",
        )
        if filename:
            export_frames(filename, self.frames)
            self.status_label.setText(f"Sesja zapisana: {Path(filename).name}")
