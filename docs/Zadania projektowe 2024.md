

1.Realizacja animowanej wizualizacji ramienia robota
Zrealizować sterowalną przez użytkownika wizualizację wybranego ramienia robota (przykłady ramion
poniżej).Wizualizowane ramię (zwane dalej również modelem) musi posiadać co najmniej 3 stopnie swobody
(wizualizacja manipulatora nie jest konieczna ani nie jest wliczana do stopni swobody). Ruchy elementów
ramienia powinny odzwierciedlać rzeczywiste ruchy robota (np. kąt obrotu złącza w rzeczywistości jest
limitowany i nie może znacznie przekraczać kąta 360
o
## ).
Wizualizowane ramię powinno umożliwiać interakcję z przynajmniej jednym elementem  wirtualnego otoczenia
(elementem takim może być prymityw, czyli sfera bądź kostka), polegającą na przemieszczaniu tego elementu
(chwycenie, przemieszczenie, pozostawienie).
Interfejs sterujący powinien umożliwiać poruszanie poszczególnymi złączami bezpośrednio (w wyniku
naciśnięcia odpowiednich klawiszy), lecz również powinna istnieć możliwość wprowadzania położenia w
postaci liczbowej (wówczas ramie powinno wykonać animowany ruch do nowej pozycji). W przypadku ramion
cylindrycznego i polarnego, XY jest obligatoryjne).
Dodatkowo program powinien umożliwiać pracę w trybie uczenia i pracy – tak jak to ma miejsce w przypadku
„prawdziwych” robotów przemysłowych. Przykładowo: ramię robota w trybie uczenia przemieszcza
„prymitywa” z udziałem użytkownika, a po „nauczeniu” powtarza sekwencję ruchów.

Robot typu „articulated arm”.

Robot polarny (kulisty) i cylindryczny.

2.Zrealizować wizualizację mieszaniny 2-wymiarowych rozkładów gaussowskich
„Mieszanina gaussowska” jest ważoną sumą rozkładów Gaussa o określonych parametrach (wartość średnia,
macierz kowariancji). Jest to często spotykany sposób przybliżania rozkładów o bardziej złożonym
charakterze.
Program ma wizualizować rozkład sumy n rozkładów o podanych parametrach i wagach.
Dodatkowo powinna istnieć możliwość opcjonalnego zilustrowania obecności „impulsów szpilkowych” o
podanej lokalizacji na płaszczyźnie.
Program powinien umożliwiać oglądanie wykresu pod różnymi kątami i zmianę kierunku padania światła.
3.Zrealizować wizualizację „przekroju gęstości” mieszaniny 3-wymiarowych rozkładów
gaussowskich
„Mieszanina gaussowska” jest ważoną sumą rozkładów Gaussa o określonych parametrach (wartość średnia,
macierz kowariancji). Jest to często spotykany sposób przybliżania rozkładów o bardziej złożonym
charakterze.
Program ma wizualizować rozkład gęstości przekroju sumy n 3-wymiarowych rozkładów o podanych
parametrach i wagach w przecięciu określoną płaszczyzną. Wynik ma być prezentowany jako 3-wymiarowy
wykres, z możliwym wyborem kąta obserwacji. Płaszczyzna tnąca przestrzeń zawierającą mieszaninę
rozkładów musi mieć możliwość zmiany swojej orientacji, co najmniej w trzech pozycjach wyznaczony przez
osie XY, XZ i YZ (najlepiej, gdy pozwoli na swobodną orientację) i przesuw wzdłuż osi (w uproszczonym
przypadku wzdłuż odpowiednio osi Z, Y i X).
4.Gra zręcznościowa
Gra stworzona z wykorzystaniem detekcji kolizji między obiektami. Przed realizacją należy uzgodnić
scenariusz gry. Mile widziana „praca w sieci”.
Gra powinny pozwalać zapis i odtworzenie przebiegu gry. W grach „dynamicznych” może to być zapis
pozwalający na odtworzenie kilku sekund poprzedzających wciśnięcie wybranego klawisza; odtworzenie
powinno być możliwe po zakończeniu gry (lub jej etapu).
5.3D wizualizacja danych 2D
Stworzyć program pozwalający na trójwymiarową prezentacje danych zapisanych w postaci bitmapy. Wartość
jasności bitmapy ma zostać przetworzona na wysokość wykresu wizualizowanych danych. Program
zoptymalizować do pracy z dużymi zbiorami danych. Program powinien pozwolić na wybór oświetlenia i
powierzchni wynikowej powierzchni.
6.Wizualizacja pracy drukarki 3D, obrabiarki (frezarka/tokarka)
Stworzyć animowany model prezentujący działanie urządzenia.
7.Wizualizacja gry w szachy (lub podobnej)
Stworzyć animowany model szachownicy umożliwiający grę i/lub odtwarzanie przebiegu partii.
8.Wizualizacja urządzenia mechanicznego
Takiego jak zegar, silnik tłokowy, maszyna parowa.
9.Edytor obrazów bitmapowych sterowany grafem
Edytor obrazów, w którym sposób przetwarzania obrazu ustalany jest poprzez łączenie ze sobą bloczków
realizujących standardowe bloki przetwarzające obraz.
10.Konwerter schematu logicznego na funkcję logiczną
Program pozwalający na edycję schematu logicznego z wykorzystaniem symboli graficznych, zamieniający
ten schemat na postać tekstową. Schemat powinien obejmować podstawowe funktory logiczne (bez
przerzutników synchronicznych)

## Ocena:
Wpływ na ocenę projektu będą miały:
jakości i estetyka wizualizacji (~10p);
ergonomia i wygody sterowania interfejsu/klawiatury/myszki (~10p);
ocena jakości realizacji możliwości „programowego” sterowania modelem (w trybie „uczenia” i
„wykonywania” dla robota), odtwarzania etapów (w grach), cofanie (programy inne) itp. – (~10p);
„sprawność” kodu i wykorzystanie zaawansowanych funkcji/metod (np. wykrywanie kolizji) – (~20p);
dodatkowe elementy (np. wykorzystanie sieci, racjonalne użycie strumienia audio/wideo itp.) – (~10p);
Dokumentacja (papierowa) oceniana jest za opis struktury programu – (~15p);
Komentarze, przejrzystość kodu i ew. wykorzystanie mechanizmów tworzenia dokumentacji – (~15p).
Ocena dokonywana jest na podstawie realizacji:
•opracowania założeń realizacji (data rozpoczęcia +2tygodnie) – 10p. Założenia muszą uwzględniać
zagadnienia obiektowości;
•sprawozdanie z realizacji projektu (data rozpoczęcia +4tygodnie) – 20p. Sprawozdanie obejmuje opis
zrealizowanych elementów projektu (projekt interfejsu, elementy właściwego programu);
•realizacja końcowa (najpóźniej pierwsze 2..3 dni sesji) – prezentacja działającego projektu wraz ze
sprawozdaniem zawierającym  opis programu, jego architekturę itp. – 70p
Dopuszczona jest realizacja za pomocą pakietów oprogramowania:
•aktualnie rozwijanych;
•umożliwiających sterowanie modelem za pomocą powszechnie stosowanych języków wysokiego
poziomu (C/C++, C#, Python, Java).