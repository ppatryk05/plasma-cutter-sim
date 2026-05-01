# Symulator Wycinarki Plazmowej

Projekt zaliczeniowy – symulacja 3D robota kartezjanskiego (wycinarki plazmowej).  
Renderowanie OpenGL, blacha z tekstura, iskry, siatka podloza, pelny HUD.

## Wymagania

- **Python 3.10+** (testowane na 3.14)
- pip

## Uruchomienie

```bash
pip install -r requirements.txt
python main.py
```

`requirements.txt` zainstaluje wszystko automatycznie:
- `pygame-ce` – okno, eventy, czcionki
- `numpy` – siatka blachy
- `PyOpenGL` + `PyOpenGL_accelerate` – rendering 3D

## Sterowanie

| Klawisz | Akcja |
|---|---|
| Strzalki | ruch glowicy |
| Shift (trzymaj) | predkosc 400 mm/s |
| Ctrl (trzymaj) | predkosc precyzyjna 80 mm/s |
| Spacja | wlacz / wylacz plazme |
| C | wyczysc blache |
| R | reset glowicy do centrum |
| LPM + ruch myszy | obrot kamery |
| Scroll | zoom |
| Esc | wyjscie |
