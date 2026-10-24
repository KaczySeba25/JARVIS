# Jarvis — punkt wznowienia pracy

**Ostatnia aktualizacja:** 2026-10-24
**Folder projektu:** `C:\Jarvis`  
**Jezyk rozmowy z Sebastianem:** polski, prosty i bez niepotrzebnego zargonu.

## O co chodzi w Jarvisie

Jarvis ma byc uniwersalnym pomocnikiem pracujacym na komputerze i w internecie. Ma rozumiec zwykle polecenia, zdobywac potrzebna wiedze, przygotowywac plan, wykonywac uzgodnione kroki, naprawiac bledy i pokazywac dowody rezultatu. Nie jest z gory systemem do sklepu, tradingu, SaaS ani zadnej innej branzy. To przyklady trudnych zadan, ktore Jarvis ma kiedys umiec wykonac na zlecenie. Jarvis nie steruje inteligentnym domem.

## Jak ma wygladac wspolpraca

Przy wiekszym lub nowym zadaniu Jarvis robi dokladny research, porownuje rozwiazania, wybiera najlepsze i przedstawia plan wraz z mozliwymi ulepszeniami. Po akceptacji sam realizuje caly uzgodniony zakres, bez pytania o kazdy drobiazg. Gdy potrzebuje logowania, zalozenia konta lub dzialania niedostepnego w systemie, podaje Sebastianowi jasne kroki i wznawia zadanie po jego udziale. Dopytuje, gdy cel albo warunki sukcesu sa niejasne. Pokazuje dowod dopasowany do zadania i uczciwie mowi, czego nie mogl sprawdzic.

Jarvis powinien rozwijac ogolne zdolnosci: research, planowanie, programowanie, tworzenie narzedzi, prace z plikami i uslugami online, uczenie nowych dziedzin, bezpieczne poprawianie siebie, pamiec i ocene wlasnych wynikow. Przykladami przyszlych sprawdzianow sa budowa narzedzia dla wskazanego klienta, przygotowanie specjalizowanego agenta na zlecenie albo opanowanie nowej uslugi internetowej. Nie wolno zamieniac przykladow w stale specjalizacje lub ustawienia.

## Stan kodu

W tej sesji poprawiono router modeli: po błędzie skonfigurowanej usługi online Jarvis próbuje
przełączyć się na dostępny lokalny model Ollama, zachowując tę samą rozmowę i komunikując zmianę.
Konfiguracja nadal musi być jawna — Jarvis nie wysyła rozmów do przypadkowych „darmowych API”.
Usunięto też z repozytorium lokalny `.env`, cache Python i dane runtime; ich odpowiedniki są ignorowane
przez `.gitignore`, a wzór konfiguracji jest w `agent/.env.example`.

Etap 1 rozbudowy jest zakończony: vault używa DPAPI, waliduje identyfikatory usług, obsługuje zapis,
metadane i usuwanie, a warstwa skilla nigdy nie zwraca sekretu do modelu. Zaufane konektory mogą
czytać sekret tylko w procesie. Governance zapisuje również ustrukturyzowane lekcje z błędów,
zamiast automatycznie powtarzać nieudane działanie. Dodatkowo zapisuje bezpieczny audyt użycia,
rotacja nie ujawnia starego sekretu, a brakujące dane są pobierane przez bezpieczny formularz,
nie przez czat.

Etap 2 rozpoczęty: dodano ogólny skill `browser_operator` oparty o Playwright. Obsługuje nawigację,
inspekcję, zwykłe pola formularzy i pola sekretów przez referencję vaultu. Kliknięcia wymagają
zatwierdzonego planu; CAPTCHA, SMS, 2FA i blokady nadal wymagają człowieka.

Etap 3 rozpoczęty: `agent/recovery.py` klasyfikuje awarie, zapisuje techniczny ślad i definiuje
zamknięty zestaw bezpiecznych, maksymalnie jednokrotnych ponowień. Błędy działań zewnętrznych,
poświadczeń i blokad człowieka nie są automatycznie powtarzane.

Operator przeglądarki oznacza stronę jako `human_required`, gdy wykryje typowe CAPTCHA, 2FA,
SMS lub weryfikację. Nie próbuje tych zabezpieczeń obchodzić.

Jarvis ma również `computer_files`: kontrolowany dostęp do zatwierdzonych katalogów `C:\Jarvis`
i `D:\AI Trading Agent`. Ścieżki poza allowlistą są blokowane, odczyt redaguje typowe sekrety,
a zapis robi kopię `.jarvis-backup`. Dostęp do plików jest wysokiego ryzyka i wymaga zatwierdzonego planu.

Etap 2 domknięty technicznie: profil przeglądarki jest trwały i przechowywany lokalnie w vault,
a wykrycie CAPTCHA/SMS/2FA przełącza zadanie w `waiting_user`. Po odpowiedzi „gotowe” Jarvis
wznawia zadanie z tym samym profilem i kontekstem. Pełne połączenie OAuth nadal wymaga konkretnej,
legalnej usługi i jej zakresów uprawnień.

Rozpoczęto Etap 3: `secret_request` otwiera lokalne okno bezpiecznego przekazania danych.
Login, hasło, token lub klucz API trafia bezpośrednio do DPAPI vaultu; nie przechodzi przez
czat, pamięć ani zwykły plik.

Dodano `api_onboarding`: Jarvis może otworzyć oficjalną stronę konfiguracji API/OAuth,
przekazać użytkownikowi dokładne instrukcje, poczekać na bezpieczne zapisanie danych i wznowić
zadanie po `gotowe`. Samo otwarcie strony nie jest traktowane jako uzyskanie dostępu.

Punkt 1 z nowego zestawu 8 rozszerzeń jest wdrożony: `task_center` udostępnia trwały status,
timeline, oczekujące zgody i oczekiwanie na użytkownika dla każdego zadania.

Punkt 4 wdrożony jako działający runner: `regression_runner` wykonuje ograniczoną kompilację
Python i inwentaryzuje testy projektu, a wynik zapisuje jako wykonaną kontrolę zamiast pustej obietnicy.
Na `D:\AI Trading Agent` runner przeszedł kompilację 56 plików Python i znalazł 8 plików testowych
w 4.0 s. Utworzono osobne środowisko walidacyjne bez nadpisywania istniejących środowisk;
pełny zestaw zakończył się wynikiem `12 passed in 12.46s`. Oryginalne środowiska projektu nadal
są uszkodzone, dlatego walidator pozostaje osobnym środowiskiem.
Punkt 7 wdrożony jako bezpieczny fundament: `project_learning` zapisuje tylko fakty z inventory,
bez kopiowania treści plików, i dodaje lekcję do governance.
Punkt 8 wdrożony: `operator_mode` i `safety_policy` opisują tryb nadzorowany, wymaganie planu
i kroki wymagające człowieka.

Punkt 2 rozpoczęty: `connector_manager` rejestruje jawne konektory API/OAuth/przeglądarki wraz
z zakresem i endpointem. Nowy konektor jest domyślnie wyłączony i wymaga testu połączenia.

Dashboard otrzymał panel `Konektory...` z lokalnym katalogiem usług (m.in. YouTube, Google,
GitHub, Outlook, Slack, Shopify i Binance Testnet), wyszukiwaniem oraz rejestracją własnego
konektora. Katalog zawiera wyłącznie metadane i oficjalne adresy dokumentacji; nie przechowuje
sekretów, nie włącza dostępu sieciowego i nie zastępuje konfiguracji OAuth/API ani testu połączenia.

Próba uruchomienia Jarvisa z zadaniem przygotowania legalnego agenta YouTube została wykonana w
lokalnym środowisku. Router poprawnie wykrył Ollama i model `qwen3.5:4b`, utworzył zadanie oraz
zapisał etap planowania. Generowanie odpowiedzi nie zakończyło się w rozsądnym czasie na CPU,
więc próbę zatrzymano bez działań zewnętrznych. Nie deklaruję ukończenia zadania YouTube ani
utworzenia konta; wymaga to działającego modelu o akceptowalnej szybkości, konkretnego OAuth
Google/YouTube i późniejszej akceptacji planu.

Router modeli został następnie wzmocniony: w trybie auto porządkuje lokalne modele według
przydatności i przewidywanego kosztu CPU, nie wybiera arbitralnie dużego modelu, ma ograniczony
timeout oraz przechodzi do kolejnego jawnie skonfigurowanego providera/modelu po błędzie. Obsługiwane
są skonfigurowane źródła Groq, Gemini, OpenAI i Ollama; router nie odkrywa przypadkowych darmowych
API. Konektor manager ma akcję `ensure`, która przygotowuje metadane usługi z katalogu lub z
oficjalnego endpointu, ale nie tworzy sekretu, konta ani fałszywego statusu połączenia.

Naprawiono również aktywne zadanie YouTube. Przyczyną wcześniejszego zatrzymania był wycofany
model Groq `llama3-70b-8192`; router odpytał aktualną listę providera i wybrał dostępny
`openai/gpt-oss-20b`. Nowe zadanie utworzyło task `cdd7bd0d5a294e139d9a5ba356d04850`,
przeszło planowanie i zatrzymało się na `waiting_approval` przed onboardingiem OAuth oraz
działaniami zewnętrznymi. To oznacza prawidłowe działanie bramki bezpieczeństwa, a nie awarię.
Poprawiono też polskie napisy dashboardu, w tym znaki diakrytyczne i symbole menu.

Przekazano również zatwierdzenie planu YouTube (`zatwierdzam plan`). Jarvis przyjął zgodę,
ale pełna realizacja ponownie okazała się zbyt wolna przy dużym promptcie na dostępnej konfiguracji.
Router otrzymał większy budżet odpowiedzi i niski poziom reasoning dla GPT-OSS; wykonanie agenta
YouTube nadal nie jest ukończone i nie wykonano publikacji ani działań na koncie.

Dodano ograniczoną naprawę protokołu planu: jeżeli model dla zadania YouTube zwróci kroki, ale
pominie zakres lub listę narzędzi, Jarvis może uzupełnić wyłącznie bezpieczny zakres researchu,
metadanych konektora i lokalnego projektu. Nie rozszerza to uprawnień do konta, publikacji ani
płatności. Kolejna próba autonomicznego uruchomienia zakończyła się błędem providera modelu przed
decyzją, więc zadanie nie zostało przedstawione jako ukończone.

Skrócono również listę skilli w promptcie systemowym z pełnych opisów do zwartego katalogu nazw,
ryzyka i trybu sieciowego. Ma to zmniejszyć zużycie kontekstu oraz opóźnienie planowania, bez
odbierania modelowi informacji o dostępnych narzędziach. Próba po tej zmianie nadal nie dała
decyzji w rozsądnym czasie na aktualnym providerze, więc agent YouTube pozostaje nieukończony.

Podczas wznowienia etapowego Jarvis poprawnie doszedł do wywołania `connector_manager`. Pierwsze
wywołanie ujawniło, że model czasem przekazuje naturalny tekst zamiast JSON; parser konektora został
uodporniony na samą nazwę usługi lub zdanie zawierające znaną usługę, bez zwiększania uprawnień.

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
