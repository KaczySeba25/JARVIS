# Imperium Cloner - rozklad na czesci pierwsze

## 1. Czym jest Cloner

Imperium Cloner to narzedzie do analizy cudzych produktow, aplikacji i narzedzi SaaS.
Jego zadanie nie polega na kopiowaniu calej strony 1:1, tylko na:

- rozpoznaniu czym dane narzedzie faktycznie jest,
- zebraniu jego realnych funkcji,
- odrzuceniu marketingowego szumu,
- zapisaniu wyniku jako blueprint do dalszej budowy nowego produktu.

Cloner jest warstwa analityczna i decyzyjna.
To on odpowiada na pytanie:

"Co to narzedzie naprawde potrafi i co z tego warto przeniesc dalej?"

## 2. Glowny cel Clonera

Glowny cel Clonera to zamiana:

- linku do strony,
- nazwy narzedzia,
- albo wskazanego produktu

na uporzadkowana liste realnych funkcji, ktore da sie:

- obejrzec,
- wybrac,
- zapisac,
- przekazac do Generatora SaaS.

## 3. Co Cloner przyjmuje na wejsciu

Cloner powinien umiec przyjac:

- URL strony produktu,
- nazwe produktu lub narzedzia,
- tryb pracy: dla siebie / na sprzedaz,
- jezyk,
- region,
- dodatkowe notatki operatora.

W praktyce oznacza to, ze operator nie musi wiedziec jak zbudowane jest dane narzedzie.
Wystarczy, ze poda adres albo nazwe.

## 4. Co Cloner robi krok po kroku

### 4.1. Rozpoznanie zrodla

Najpierw Cloner ustala:

- czy dostal URL czy tylko nazwe,
- jaka strona jest prawdziwa strona produktu,
- czy domena jest poprawna,
- czy nie jest to parked domain, strona sprzedazowa albo przypadkowy wynik.

### 4.2. Pobranie materialu

Potem zbiera dane ze strony:

- tresc strony glownej,
- sekcje funkcji,
- opis produktu,
- naglowki,
- elementy typu pricing, solutions, features, workflows,
- dodatkowe podstrony, jesli daja realne informacje.

### 4.3. Identyfikacja funkcji

Potem Cloner probuje rozpoznac:

- co jest faktyczna funkcja,
- co jest tylko haslem marketingowym,
- co jest jedynie benefitem,
- co jest wzmianka o zewnetrznym narzedziu, a nie funkcja produktu.

### 4.4. Filtrowanie jakosci

To jest kluczowy etap.
Cloner nie powinien zwracac bzdur typu:

- hasla reklamowe,
- polityki platnosci,
- slogany typu "grow faster",
- pojedyncze zdania bez znaczenia funkcjonalnego.

Ma zostawic tylko:

- funkcje rzeczywiste,
- umiejetnosci produktu,
- konkretne mozliwosci operacyjne.

### 4.5. Zapis blueprintu

Na koncu Cloner zapisuje wynik jako blueprint.
Blueprint zawiera:

- nazwe produktu,
- zrodlo,
- status jakosci,
- liste funkcji,
- dodatkowe metadane potrzebne Generatorowi.

## 5. Co jest wyjsciem Clonera

Najwazniejszym wyjsciem Clonera jest blueprint.

Blueprint powinien zawierac:

- realne funkcje produktu,
- opis co funkcja robi,
- poziom pewnosci,
- informacje czy funkcja jest sensowna do wdrozenia,
- wynik gotowy do zaznaczania i wyboru.

To nie jest raport dla raportu.
To jest material produkcyjny dla Generatora.

## 6. Co juz mamy w Clonerze

Na teraz mamy:

- lokalny projekt `imperium-cloner-v1`,
- analize po URL i po nazwie,
- lepsze wykrywanie prawidlowej domeny,
- odrzucanie parked domains i zlych kandydatow,
- filtrowanie marketingowego szumu,
- quality gate dla funkcji,
- zapis blueprintow do plikow JSON,
- realne testy na takich produktach jak `Helium 10` i `Base44`.

## 7. Mocne strony Clonera

- rozdziela funkcje od marketingu,
- zapisuje wynik do dalszego wykorzystania,
- pozwala wybierac tylko potrzebne funkcje,
- jest baza pod budowe nowych narzedzi,
- dziala jako etap research + specyfikacja.

## 8. Slabe strony i ograniczenia

- nie wszystko da sie wyczytac tylko ze strony glownej,
- niektore produkty ukrywaja funkcje po zalogowaniu,
- niektore funkcje wymagaja analizy flow, a nie samego tekstu,
- nie kazda funkcja jest od razu gotowa do natychmiastowego zakodowania,
- jako analiza bezpośrednia nadal wymaga dobrego source material.

## 9. Co Cloner powinien robic docelowo jeszcze lepiej

- analizowac wiecej podstron automatycznie,
- rozpoznawac workflow produktu, a nie tylko listy funkcji,
- lepiej grupowac funkcje w moduly,
- rozrozniaac funkcje podstawowe, premium i wspierajace,
- oznaczac trudnosc wdrozenia,
- oznaczac zaleznosci miedzy funkcjami,
- sugerowac co mozna zbudowac za darmo, a co wymaga kosztow.

## 10. Najkrotsza definicja Clonera

Cloner bierze cudzy produkt i zamienia go na:

- realne funkcje,
- logiczny blueprint,
- material gotowy do budowy nowego SaaS.
