# Jarvis — punkt wznowienia pracy

**Ostatnia aktualizacja:** 2026-10-02  
**Folder projektu:** `C:\Jarvis`  
**Jezyk rozmowy z Sebastianem:** polski, prosty i bez niepotrzebnego zargonu.

## O co chodzi w Jarvisie

Jarvis ma byc uniwersalnym pomocnikiem pracujacym na komputerze i w internecie. Ma rozumiec zwykle polecenia, zdobywac potrzebna wiedze, przygotowywac plan, wykonywac uzgodnione kroki, naprawiac bledy i pokazywac dowody rezultatu. Nie jest z gory systemem do sklepu, tradingu, SaaS ani zadnej innej branzy. To przyklady trudnych zadan, ktore Jarvis ma kiedys umiec wykonac na zlecenie. Jarvis nie steruje inteligentnym domem.

## Jak ma wygladac wspolpraca

Przy wiekszym lub nowym zadaniu Jarvis robi dokladny research, porownuje rozwiazania, wybiera najlepsze i przedstawia plan wraz z mozliwymi ulepszeniami. Po akceptacji sam realizuje caly uzgodniony zakres, bez pytania o kazdy drobiazg. Gdy potrzebuje logowania, zalozenia konta lub dzialania niedostepnego w systemie, podaje Sebastianowi jasne kroki i wznawia zadanie po jego udziale. Dopytuje, gdy cel albo warunki sukcesu sa niejasne. Pokazuje dowod dopasowany do zadania i uczciwie mowi, czego nie mogl sprawdzic.

Jarvis powinien rozwijac ogolne zdolnosci: research, planowanie, programowanie, tworzenie narzedzi, prace z plikami i uslugami online, uczenie nowych dziedzin, bezpieczne poprawianie siebie, pamiec i ocene wlasnych wynikow. Przykladami przyszlych sprawdzianow sa budowa narzedzia dla wskazanego klienta, przygotowanie specjalizowanego agenta na zlecenie albo opanowanie nowej uslugi internetowej. Nie wolno zamieniac przykladow w stale specjalizacje lub ustawienia.

## Stan kodu

Przeczytaj nastepnie:

1. `README.md` — uruchamianie i ogolny opis.
2. `JARVIS_VISION.md` oraz `USER_PROJECT_CONTEXT.md` — uzgodniona wizja i kontekst.
3. `IMPLEMENTED_FEATURES.md` i `FINAL_AUDIT.md` — co istnieje oraz znane ograniczenia.
4. `ROADMAP.md` i `NEXT_10_TASKS.md` — kierunki dalszej pracy.

W projekcie sa m.in. lokalne plany zadań i historia postepu, pamiec z mozliwoscia przegladu i edycji, narzedzia do pracy w katalogu `workspace`, lokalne wersje plikow, ograniczone uruchamianie projektow oraz reczne przekazanie logowania uzytkownikowi. Wiele skilli pozostaje wczesnymi pomocnikami lub szkicami.

## Ograniczenia, ktorych nie wolno ukrywac

- Nie ma uniwersalnych polaczen OAuth/API ani gotowych polaczen do poczty, sklepow, publikacji w mediach spolecznosciowych czy handlu na zywo.
- Uruchamianie wygenerowanego kodu nie jest pelnym sandboxem Windows.
- Zgoda na plan nie ogranicza jeszcze osobno kazdego adresata, pola formularza ani kwoty.
- Dowody z narzedzi nie zawsze oznaczaja niezaleznie potwierdzony rezultat w zewnetrznej usludze.
- Wyszukiwanie pamieci jest proste i lokalne, nie jest pelnym wyszukiwaniem semantycznym.
- Sama obecnosc skilla nie oznacza, ze jest kompletny lub ekspercki.
- Ostatni audyt odnotowuje kompilacje skladni Pythona; pelny zestaw testow i prawdziwe integracje nie byly wtedy uruchomione.

## Materialy i wersje dokumentow

Wczesniejsze notatki o Imperium, generatorze, SaaS, tradingu, sklepie i opisie Jarvisa sa zarchiwizowane w `reference\historical_user_documents\`. Wiele plikow ma date sprzed projektu Jarvis. Niektore sa powielone, nieaktualne lub sprzeczne z pozniejszymi ustaleniami. Traktuj je jako material do zrozumienia historii i pomyslow, nie jako instrukcje dla Jarvisa. Zestawienie i sumy plikow sa w `reference\historical_user_documents\INDEX.md`.

Stary plik `JARVIS_STATE_CHECKPOINT.md` zawieral bledny, sztywny kierunek biznesowy i zostal usuniety, aby nie mylil kolejnych sesji. Nie odtwarzaj go z kopii. W razie rozbieznosci ten plik i `JARVIS_VISION.md` maja pierwszenstwo.

## Dla kolejnej rozmowy/modelu

Kontynuuj prace od tego pliku. Najpierw obejrzyj aktualny kod i stan zmian, potem sprawdz najwazniejsze polaczenia miedzy funkcjami i poprawiaj problemy. Przed koncem aktualizuj ten punkt wznowienia oraz dokumenty opisujace zmienione funkcje. Nie zakladaj, ze historia czatu bedzie dostepna.
