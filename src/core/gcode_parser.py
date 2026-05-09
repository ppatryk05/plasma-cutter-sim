from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from .types import MotionCommand


def _strip_comments(line: str) -> str:
    if ";" in line:
        line = line.split(";", maxsplit=1)[0]
    return line.strip()


def parse_gcode_lines(lines: Iterable[str]) -> List[MotionCommand]:
    commands: List[MotionCommand] = []
    for raw_line in lines:
        clean = _strip_comments(raw_line)
        if not clean:
            continue
        parts = clean.split()
        if not parts:
            continue

        name = parts[0].upper()
        params: dict[str, float] = {}
        for token in parts[1:]:
            if len(token) < 2:
                continue
            letter = token[0].upper()
            try:
                value = float(token[1:])
            except ValueError:
                continue
            params[letter] = value

        if name in {"G0", "G1"}:
            commands.append(
                MotionCommand(
                    kind=name,
                    x=params.get("X"),
                    y=params.get("Y"),
                    z=params.get("Z"),
                    e=params.get("E"),
                    f=params.get("F"),
                )
            )
        elif name in {"M104", "M109"}:
            commands.append(MotionCommand(kind=name, nozzle_temp=params.get("S")))
        elif name in {"M140", "M190"}:
            commands.append(MotionCommand(kind=name, bed_temp=params.get("S")))
    return commands


def parse_gcode_file(path: str | Path) -> List[MotionCommand]:
    source = Path(path)
    return parse_gcode_lines(source.read_text(encoding="utf-8").splitlines())
