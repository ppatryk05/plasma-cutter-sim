# Implementacja zadania 6 - drukarka 3D

## Moduły

- `src/core/gcode_parser.py` - parsowanie `G0/G1` i komend temperatur.
- `src/core/kinematics.py` - model ruchu osi z limitami roboczymi.
- `src/core/thermal_model.py` - uproszczony model nagrzewania i chłodzenia.
- `src/core/material_model.py` - akumulacja segmentów ekstruzji.
- `src/sim/collision.py` - walidacja granic i podstawowe ostrzeżenia bezpieczeństwa.
- `src/sim/simulator.py` - pipeline kroków symulacji i generowanie klatek.
- `src/render/scene3d.py` - wizualizacja 3D głowicy, ścieżki i depozytu.
- `src/ui/main_window.py` - GUI, sterowanie, wykresy i replay.
- `src/io/session_replay.py` - zapis/odczyt przebiegu symulacji.

## Obiektowość

Logika została rozdzielona na klasy odpowiedzialne za pojedyncze domeny:
- parser wejścia,
- silnik kinematyki,
- model termiczny,
- model depozytu materiału,
- detektor kolizji,
- orchestrator symulacji.

## Odtwarzanie sesji

Replay serializuje komplet klatek (`state + issues`) do JSON i pozwala odtworzyć przebieg bez ponownego parsowania G-code.
