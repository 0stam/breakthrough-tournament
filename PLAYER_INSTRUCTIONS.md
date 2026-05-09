# Instrukcje dla graczy

## Wstęp

Organizuję ten turniej dla ludzi, więc nie jest moim celem przestrzeganie zasad w imię zasad. W szczególności chcielibyśmy uniknąć:

https://xkcd.com/499/

Także jakby były jakieś problemy, kogoś rozwiązanie się nie odpalało itp., to zawsze będę się najpierw próbował dogadać. Mimo to jakieś zasady są potrzebne, także zapraszam do lektury.

## Terminologia

**Gracz**: proces gracza

**Turniej**: proces/oprogramowanie zarządzające turniejem

## Informacje ogólne

**Sposób komunikacji:** standardowe wejście wyjście

**Dopuszczalne formaty ruchu:** cała plansza albo same koordynaty ruszanego pionka

**Sposób przesłania rozwiązania:** obraz Dockerowy

**Ograniczenia:** gracz mają ograniczony czas na ruch i inne fazy działania programu, a także ograniczony dostęp do zasobów

## Modyfikacje zasad

Jeśli gracz zbije wszystkie pionki przecinika, natychmiast wygrywa. Reszta zasad jest zgodna z opisem na liście.

## Komunikacja

W uproszczeniu komunikacja ma następujący przebieg:

1. Gracz deklaruje, w jakim formacie chce odbierać/wysyłać ruchy
2. Turniej wysyła graczowi, czy gra białymi/czarnymi oraz rozmiar planszy
3. Sekwencja ruchów

- gdy następuje tura gracza, turniej wysyła do niego obecny stan planszy albo ruch przeciwnika
- gracz wysyła swój ruch w wybranych formacie

Sekwencja powtarza się, aż któryś z graczy wygra.

## Deklaracja formatu

Natychmiast po uruchomieniu, gracz powinien wypisać linię:

`{format ruchu na wejściu} {format ruchu na wyjściu}`

Gdzie format ruchu to:
0 - cała plansza
1 - tylko koordynaty ruchu

Przykłady:

`0 0` - gracz chce przyjmować na wejściu i wysyłać całą planszę

`0 1` - gracz chce przyjmować na wejściu całą planszę i wysyłać tylko koordynaty ruchu

Błędne przykłady:
`0` - brakuje jednej cyfry
`Kocham bazy danych` - gracz ma udar

## Dopuszczalne formaty ruchu

### 0 - cała plansza

**UWAGA:** gracz biały w pierwszym ruchu i tak dostanie na wejściu ten format (bo przeciwnik nie zrobił jeszcze ruchu). Jeśli nie chce go przetwarzać, może go po prostu zignorować i stworzyć planszę samemu.

**UWAGA:** **nie chcesz używać tego formatu**. Na liście jest on słabo zdefiniowany, więc moja interpretacja na pewno różni się od twojej. Dużo prościej będzie przystosować rozwiązanie do formatu 1 opisanego poniżej.

**UWAGA:** wprowadziłem tu tylko jedną autorską modyfikację. Kolejne linie planszy są oddzielone spacją, a nie enterem. Wyjaśnienie jest w sekcji `Sekwencja ruchów`. W tym opisie dla uproszczenia będę podawał obie wersje: z enterami - czytelne dla człowieka, i bez enterów - w formacie obsługiwanym przez turniej.

Zgodnie z listą, na planszy mamy różne typy pól:

B - gracz pierwszy, biały (!!!)

W - gracz drugi, czarny (!!!)

\_ - puste pole

o - pole, z którego został wykonany ostatni ruch

Planszę wypisujemy zgodnie z rysunkiem na liście, czyli czarny gracz jest na górze, a biały na dole. Przykład dla planszy 6x6

Format z enterami:

```
W W W W W W
W W W W W W
_ _ _ _ _ _
_ _ _ _ _ _
B B B B B B
B B B B B B
```

Format obsługiwany przez turniej:

```
W W W W W W W W W W W W _ _ _ _ _ _ _ _ _ _ _ _ B B B B B B B B B B B B
```

Czyli po ruchu gracz białego plansza może wyglądać następująco

Format z enterami:

```
W W W W W W
W W W W W W
_ _ _ _ _ _
_ _ _ B _ _
B B B o B B
B B B B B B
```

Format obsługiwany przez turniej:

```
W W W W W W W W W W W W _ _ _ _ _ _ _ _ _ B _ _ B B B o B B B B B B B B
```

Zwróć uwagę, że:

- oznaczenia W/B są przeciwne, niż można by się spodziewać po nazwie
- przy zapisie tego formatu jako tablica, współrzędne nie zgrywają się ze współrzędnymi, których można by się spodziewać po planszy szachowej
- jeśli twój program ma inne założenia co do kierunku osi/kolejności linii, w przypadku samych współrzędnych da się to bardzo prosto naprawić, a w przypadku wczytywania całej planszy nie jest to takie proste
- symbol pola, z którego został wykonany ruch, jest bezużyteczny (z wielu powodów)

Także jeszcze raz powtarzam, że prawdopodobnie prościej będzie użyć współrzędnych ruchów.

Jeśli jednak zdecydujesz się na ten format, **dowolne odstęstwa od niego są traktowane jako błędny ruch**.

### 1 - tylko koordynaty ruchu

Koordynaty ruchu mają następującą postać:

`{x pola starowego} {y pola startowego} {x pola docelowego} {y pola docelowego}`

Kierunki osi działają jak na planszy szachowej, to znaczy:

- A, B, C zmienia się w 0, 1, 2 na osi X
- 1, 2, 3 zmienia się w 0, 1, 2 na osi Y
- po ruchu gracza białego, współrzędna y jego pionka zmienia się o +1
- po ruchu gracza czarnego, współrzędna y jego pionka zmienia się o -1

Czyli na początku gry na planszy 8x8:

- gracz biały ma pionki na współrzędnych (0, 0), (1, 0), ..., (7, 0) oraz (0, 1), (1, 1), ..., (7, 1)
- gracz czarny ma pionki na współrzędnych (0, 6), (1, 6), ..., (7, 6) oraz (0, 7), (1, 7), ..., (7, 7)

Jeśli twój program używa innych współrzędnych, prawdopodobnie da się je przekonwertować dwiema operacjami dodawania/odejmowania

Przykład:

`0 1 1 2` - gracz biały ruszył się swoim pionkiem do przodu na ukos

`5 5 5 4` - gracz czarny ruszył się swoim pionkiem do przodu

## Informacje o planszy

Gdy gracz zadeklaruje się, jakich formatów chce używać, turniej wysyła do niego:

`{rozmiar planszy x} {rozmiar planszy y} {id gracza}`

Gdzie `{id gracza}`:

- 0 - biały
- 1 - czarny

Przykład:

`8 7 0` - plansza o szerokości 8, wysokości 7, gracz biały

`8 8 1` - plansza 8x8, gracz czarny

## Sekwencja ruchów

### Obecny stan planszy

Przed każdym ruchem turniej wysyła graczowi obecny stan planszy w wybranym formacie:

- cała plansza, jeśli gracz wybrał format 0 lub **to jest pierwsz ruch gracza białego**
- tylko koordynaty ostatniego ruchu, w przeciwnym wypadku

_INFO:_ od tego momentu liczony jest limit czasu na ruch

### Ruch gracza

Gracz ma ograniczony czas na ruch. W zależności od implementacji, ograniczenie jest irytujące dla graczy albo prowadzącego tuniej. Spróbowałem zrobić pewną hybrydę.

Załóżmy, ża na ruch jest 1s. Pojawia się problem, że gracze muszą zgadywać, np. jaką głębokość drzewa program da radę zbadać, zanim upłynie ten czas. Jeden zawodnik może np. ustawić głębokość 5 i na styk się zmieścić. Drugi może ustawić 5, po czym przegrać przez przekroczenie czasu. Trzeci znowu może ustawić bezpieczne 3 i przegrać z tym, który ustawił 5.

Żeby rozwiązać ten problem, podczas swojego czasu na ruch program może wypisać dowolną ilość linii z ruchem, a turniej zapisze ostatnią pełną linię (pełna linia kończy się enterem).

_INFO:_ z tego wynika lekka zmian w formacie 0 względem listy, naprawdę upraszcza to implementację.

Tutaj opis podzielę na kilka ścieżek

#### Ścieżka 1 - masz pewność, że twój program wypisze ruch w limicie czasowym

Nie musisz nic kombinować. Wystarczy, że po otrzymaniu na wejściu ruchu przeciwnika, twój program wypisze swój ruch w limicie czasowym. Nie musisz robić żadnej rozbudowanej implementacji. Wszyscy są szczęśliwi.

Tylko ustaw bezpieczną głębokość.

#### Ścieżka 2 - nie masz pewności, że twój program wypisze ruch w limicie czasowym, ale nie chcesz tryhardować

Zacznij od wypisania jakiegokolwiek ruchu, a potem szukaj tego dobrego.

**UWAGA:** ta opcja może nie zadziałać, jeżli głębokość będzie o wiele za duża. Np rozważmy taką sytuację:

- gracz wypisuje pierwszy znaleziony ruch i zaczyna liczyć
- gracz nie zdążył policzyć i zaczęło się tura przeciwnika
- przeciwnik wysłał swój ruch
- gracz nadal nie zdążył policzyć i nie zdąża do końca swojego ruchu, więc przegrywa

Także jeśli drzewo będzie bardzo głębokie, to ciągle możecie się przejechać.

#### Ścieżka 3 - chcesz tryhardować

Turniej działa następująco:

- turniej wysyła graczowi poprzedni stan planszy
- turniej zaczyna liczyć czas na ruch
- gracz wypisuje ruchy
- turniej na bieżąco zczytuje linie wysyłane przez gracza
- gdy czas na ruch mija, turniej sprawdza ostatnią pełną linię (zakończoną enterem) i zapisuje ją jako ruch
- turniej wysyła ruch do przeciwnika
- turniej przestaje zczytywać output tego gracza i zaczyna zajmować się przeciwnikiem

Ma to kilka konsekwencji.

Przede wszystkim komunikacja między standardowym wejściem/wyjściem odbywa się przez PIPE'y linuxowe. Polecam doczytać, jeśli ktoś jest zainteresowany, ale w dużym skrócie pipe jest buforem. Jeśli program wypisuje linię na wyjście, trafia ona do tego bufora. Gdy inny program chce coś odczytać, zabiera linię z tego bufora.

Jeśli program chce coś wypisać, a PIPE jest pełny, to w większości języków zawiesza się i czeka, aż się zwolni.

Także:

- wypisywanie dużej ilości tekstu podczas swojego ruchu jest bezpieczne, bo turniej będzie go na bieżąco czytał
- wypisanie dużej ilości tekstu podczas ruchu przeciwnika jest niebezpieczne, bo turniej nie czyta go na bieżąco. Jest to element bezpieczeństwa, żeby nie próbować DDOSować turnieju podczas ruchu przeciwnika
- program może bezpiecznie wypisywać linie po tym, jak upłynął jego czas na ruch, o ile nie będzie ich za dużo. Turniej przeczyta je z bufora, po czym zapomni o nich, gdy tylko dostanie świeży ruch
- jeśli program będzie szukał ruchu dłużej niż swój czas na ruch + czas na ruch przeciwnika, prawdopodobnie ztimeoutuje w kolejnym ruchu i przegra

### Podsumowanie

**Gra z perspektywy programu może wyglądać tak:**

Gracz:

```
1 1
```

format: tylko koordynaty ruchu

Turniej:

```
6 6 0
```

plansza 6x6, gracz biały

Turniej:

```
W W W W W W W W W W W W _ _ _ _ _ _ _ _ _ _ _ _ B B B B B B B B B B B B
```

w pierwszym ruchu białego turniej zawsze wypisuje całą planszę

Gracz:

```
4 1 4 2
5 1 5 2
```

gracz wypisał najpierw jeden ruch, ale potem zmienił zdanie na inny

gracz rusza się skrajnie prawym pionem do przodu

Turniej:

```
0 4 0 3
```

przeciwnik rusza się skrajnie lewym pionem do przodu

I tak aż do wygranej któregoś z graczy. Na końcu gry programy są automatycznie zatrzymywane.

**Ten sam przykład z perspektywy gracza czarnego:**

Gracz:

```
1 1
```

format: tylko koordynaty ruchu

Turniej:

```
6 6 1
```

plansza 6x6, gracz czarny

Turniej:

```
5 1 5 2
```

od razu dostajemy pierwszy ruch białego

dostajemy tylko ostateczny ruch, a nie wszystkie wypisane

Gracz:

```
0 4 0 3
```

odpowiadamy własnym ruchem

## Sposób przesłania rozwiązania

Obraz dockerowy z rozwiązaniem. Obraz powinien jako domyślną komendę uruchamiać program z algorytmem, który będzie się komunikował według opisanego wyżej schematu.

Przykładowy Dockerfile dla mojego programu

```Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install necessary dependencies
RUN pip install --no-cache-dir numpy

# Copy the rest of the workspace
COPY . .

# Set PYTHONPATH so that imports like `src.something` work correctly
ENV PYTHONPATH="/app"

# Command to run the application with default arguments
CMD ["python", "src/main.py"]
```

W zależności od języka może się różnić, ale nie powinien być zbyt skomplikowany.

Obraz należy zbudować i zapisać używając `docker save`. Mój bardzo ograniczony research sugeruje, że `docker export` nie zapisuje komendy, z którą kontener ma wystartować, więc nie można go tu użyć.

**UWAGA:** będzie mi dużo prościej, jeśli wasz kontener będzie się nazwyał `imie_nazwisko:latest` bez polskich znaków. Nie jest to konieczne, ale uprości mi robotę.

Programy będą uruchamiane przez:

```bash
docker create --name container_name -i -m memory_limit --memory-swap self.memory_limit --cpus cpu_limit image_name
docker run  -a -i container_name
```

### Którędy przesłać rozwiązanie

Metoda jest dowolna. Możecie użyć Docker Huba. Możecie udostępnić plik na Google Drive. Być może przyjmę nawet na pendrivie.

## Ograniczenia

Czasowe:

- czas na wysłanie linii z deklaracją formatów: 1s
- czas, który turniej poczeka między wysłaniem informacji o rozmiarze planszy, a wysłaniem stanu planszy do gracza białego: 0.5s
- czas na ruch: 1s

_INFO:_ turniej zaczyna liczyć pierwszy limit już po tym, jak kontener zostanie stworzony

Zasoby:

- CPU: 3 wątki na fizycznych rdzeniach
- RAM: 8GB
- Rozmiar obrazu: 1GB

Parametry komputera, na którym będzie uruchamiany turniej, zostaną podane poza repozytorium.
