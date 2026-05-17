# Założenia projektowe – Symulator Drukarki 3D

Autor: Patryk
Data: maj 2026
Technologia: Python 3.11, PyQt6, pyqtgraph, NumPy

---

## 1. Opis projektu

Projekt to aplikacja desktopowa w Pythonie, która symuluje działanie drukarki 3D.
Użytkownik wczytuje plik G-code (czyli instrukcje dla drukarki, generowane przez
programy takie jak Cura czy PrusaSlicer) i może obserwować w oknie 3D jak głowica
drukuje model warstwa po warstwie.

Chciałem zrobić coś praktycznego – coś czego mógłbym użyć żeby sprawdzić czy
mój G-code jest poprawny zanim wyślę go do prawdziwej drukarki.

Co aplikacja robi:
- wczytuje plik .gcode i go interpretuje,
- pokazuje ruchomą głowicę w oknie 3D, rysującą ścieżkę wydruku,
- wyświetla wykresy temperatury dyszy i stołu w czasie,
- ostrzega gdy głowica wychodzi poza obszar roboczy lub próbuje
  wytłaczać przy za niskiej temperaturze,
- pozwala zatrzymać/wznowić animację i zmieniać jej prędkość,
- zapisuje sesję do pliku JSON żeby można było ją odtworzyć później.

Planowane dodatkowo:
- nagrywanie symulacji do pliku wideo (.mp4),
- wyróżnianie podpór (supportów) innym kolorem.

---

## 2. Użyte biblioteki i dlaczego je wybrałem

PyQt6 – główny framework do budowania okna aplikacji. Wybrałem go bo
dobrze integruje się z Pythonem i ma QThread do obsługi wątków oraz
QTimer który posłuży jako "silnik" animacji (co 30ms przesuwa klatkę).

pyqtgraph – biblioteka do wykresów i grafiki 3D zbudowana na OpenGL.
Używam jej modułu opengl do sceny 3D (GLViewWidget daje obsługę myszy
za darmo – obracanie, zoom, przesuwanie) oraz PlotWidget do wykresów
temperatur i ekstruzji.

NumPy – szybkie obliczenia na tablicach liczb. Przydaje się do
trzymania wierzchołków brył 3D i do interpolacji pozycji głowicy
między klatkami animacji.

Python stdlib (json, dataclasses, math, pathlib) – standardowe moduły
Pythona. json do zapisu sesji, dataclasses do ładnego definiowania
klas danych, math do geometrii, pathlib do obsługi plików.

imageio + ffmpeg (planowane) – do nagrywania symulacji. Klatki OpenGL
będę przechwytywał przez grabFramebuffer() i składał w plik .mp4.

---

## 3. Struktura projektu

Podzieliłem kod na pakiety, żeby każdy miał jedną odpowiedzialność:

  src/core/   – parsowanie G-code, kinematyka, modele temp. i materiału
  src/sim/    – łączy core w całość, produkuje listę klatek animacji
  src/render/ – scena 3D (OpenGL)
  src/ui/     – okno aplikacji, przyciski, wykresy
  src/io/     – zapis i odczyt sesji JSON

Jak dane "płyną" przez program:

  Plik .gcode
      → gcode_parser  → lista poleceń (MotionCommand)
      → PrinterSimulator → lista klatek (SimulationFrame)
      → QTimer co 30ms → Scene3DWidget przesuwa głowicę
                        → PlotWidget aktualizuje wykresy

---

## 4. Główne klasy

MotionCommand – przechowuje jedno polecenie z G-code po sparsowaniu
  (np. typ G1, docelowe x/y/z, prędkość F, temperatura)

MotionState – aktualny stan maszyny w danej chwili
  (pozycja głowicy, temperatura dyszy i stołu, czas, alerty)

KinematicsEngine – oblicza nową pozycję głowicy i czas przejazdu
  po każdym poleceniu ruchu; sprawdza czy nie wychodzi poza obszar

ThermalModel – symuluje nagrzewanie/chłodzenie dyszy i stołu;
  temperatura zbliża się do docelowej stopniowo (jak w rzeczywistości)

CollisionDetector – wykrywa problemy: wyjście poza obszar roboczy,
  próba wytłaczania przy za niskiej temperaturze

PrinterSimulator – główna klasa która łączy wszystko powyżej
  i produkuje listę klatek animacji

Scene3DWidget – widżet OpenGL z modelem drukarki;
  statyczna geometria (rama, stół) tworzona raz,
  głowica przesuwana co klatkę, ścieżka wydruku rośnie inkrementalnie

MainWindow – okno główne z przyciskami, wykresami i sceną 3D

_LoadWorker – osobny wątek (QThread) do parsowania G-code;
  dzięki temu okno nie zamraża się przy dużych plikach

---

## 5. Jak rozwiązałem trudniejsze problemy

Problem: odczyt pliku G-code
G-code to zwykły tekst ale ma dużo wariantów i komentarzy.
Napisałem własny parser zamiast używać gotowej biblioteki.
Każda linia jest czyszczona z komentarzy (po ;), potem dzielona
na tokeny litera+liczba (np. X100.5 → X = 100.5). Obsługuję
polecenia G0/G1 (ruch) i M104/M109/M140/M190 (temperatury).
Komentarze slicera takie jak ;TYPE:SUPPORT będę wykorzystywał
do wykrywania podpór.

Problem: płynny ruch głowicy
G-code mówi tylko "jedź do punktu X=100 Y=50" – nie mówi jak.
Gdybym to zastosował wprost, głowica teleportowałaby się z miejsca
na miejsce. Rozwiązanie: każdy odcinek ruchu dzielę na pod-kroki
co 1 mm i interpoluję pozycję liniowo. Każdy pod-krok to osobna
klatka animacji. QTimer przesuwa indeks klatki co 30ms i głowica
płynnie jedzie zgodnie z prędkością F z G-code.

Problem: szybkość wizualizacji
Wydruk może mieć dziesiątki tysięcy punktów ścieżki. Żeby
OpenGL nie zwalniał, statyczna geometria drukarki (rama, stół)
jest tworzona raz na początku i nigdy nie zmieniana. Ścieżka
wydruku to jedna linia (GLLinePlotItem) której tablica punktów
rośnie co klatkę o jeden punkt – nie jest przebudowywana od zera.

Problem: zamrażanie okna
Przy dużym pliku G-code parsowanie i symulacja mogą trwać kilka
sekund. Żeby okno nie zamarzło, całą tę pracę wykonuję w osobnym
wątku (_LoadWorker dziedziczący po QThread). Gdy wątek skończy,
wysyła sygnał do okna głównego z gotowymi klatkami.

---

## 6. Planowane funkcje

Nagrywanie do wideo – PyQt6 ma metodę grabFramebuffer() która
zwraca aktualną klatkę OpenGL jako obraz. Zamierzam przechwytywać
każdą klatkę podczas animacji i sklejać je w plik .mp4 przez
bibliotekę imageio z backendem ffmpeg. Stworzę klasę VideoRecorder
w src/io/ z metodami start(), capture_frame() i stop().

Wizualizacja podpór – slicery (Cura, PrusaSlicer) wstawiają
w G-code komentarz ;TYPE:SUPPORT przed sekcjami supportów.
Rozszerzę parser o wykrywanie tego znacznika i będę rysował
podpory osobną linią w kolorze niebieskim, żeby odróżnić je
od właściwego modelu.

Import sesji JSON – funkcja import_frames() już istnieje w kodzie
ale nie jest podpięta do przycisku. Dodam przycisk "Wczytaj sesję"
który pozwoli otworzyć zapisany JSON bez potrzeby ponownego
parsowania G-code.

---

Dokument opisuje założenia projektowe przed pełną implementacją.
