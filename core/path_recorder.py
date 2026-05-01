from __future__ import annotations


class PathRecorder:
    """Records (x, y, plasma_on) samples from the plasma head.

    Samples are appended every simulation tick and can be iterated or
    cleared independently of the rest of the simulation.
    """

    def __init__(self) -> None:
        self._path: list[tuple[float, float, bool]] = []

    # ------------------------------------------------------------------
    def record(self, x: float, y: float, plasma_on: bool) -> None:
        """Append one sample."""
        self._path.append((x, y, plasma_on))

    def clear(self) -> None:
        """Discard all recorded samples."""
        self._path.clear()

    # ------------------------------------------------------------------
    @property
    def path(self) -> list[tuple[float, float, bool]]:
        """A copy of the recorded path as a list of (x, y, plasma_on) tuples."""
        return list(self._path)

    def __len__(self) -> int:
        return len(self._path)
