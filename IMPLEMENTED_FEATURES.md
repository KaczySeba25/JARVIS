# Aktualny stan rozbudowy Jarvisa

## Router modeli

Po błędzie skonfigurowanej usługi online Jarvis próbuje dostępnego lokalnego modelu Ollama,
zachowując bieżącą rozmowę. Nie odkrywa ani nie używa przypadkowych publicznych API bez jawnej
konfiguracji użytkownika.

## Bezpieczny vault i lekcje z błędów

Vault DPAPI przechowuje poświadczenia lokalnie, a publiczny skill zwraca tylko metadane i status.
Sekrety są dostępne wyłącznie dla zaufanego kodu konektora w procesie Jarvisa. Governance zapisuje
lekcje z błędów z ograniczoną pewnością i źródłem, aby przyszłe zadania mogły je ocenić przed użyciem.

Opis dotyczy kodu w projekcie, nie obietnicy, że wszystkie przyszłe zadania są już rozwiązane. Jarvis dobiera branżę i narzędzia do aktualnego polecenia; żaden sklep, klient ani rodzaj produktu nie jest jego domyślnym celem.

## Wdrożone podstawy

1. **Plan i zgoda:** większe zadanie może zakończyć się zapisanym lokalnie planem oczekującym na akceptację. Odpowiedź „zatwierdzam plan” wznawia go także po ponownym uruchomieniu aplikacji. Plan wygasa po 7 dniach. Działanie wymagające zmiany lub wpływu na dane jest blokowane, jeśli jego umiejętność nie została wymieniona w zaakceptowanym planie.
2. **Pamięć:** pamięć pozostaje lokalna; można ją wyszukać, wyświetlić, poprawić i usunąć. Typowe hasła i klucze są odrzucane albo redagowane przed zapisem historii.
3. **Uczenie:** aktualny research zapisuje źródła, a nowe umiejętności zachowują datę sprawdzenia, źródła i ograniczenia w manifeście wersji. Nie oznacza to, że sama walidacja importu dowodzi jakości działania umiejętności.
4. **Budowa narzędzi:** Jarvis może budować wieloplikowe projekty w `workspace/`, korzystając z zapisu plików i ograniczonych kontroli projektu. `workspace_runner` może uruchomić zatwierdzony program w widocznym oknie konsoli Windows. Stary generator masowych atrap jest wyłączony.
5. **Poprawki i cofanie:** zmiany plików mają kopie wersji; `workspace_history` potrafi przywrócić wcześniejszą wersję albo usunąć nowy plik. Umiejętności Jarvisa zachowują wersje i mogą zostać cofnięte po błędzie.
6. **Dowody:** wyniki narzędzi i kolejne etapy są zapisywane lokalnie wraz z redakcją typowych sekretów. Końcowa odpowiedź ma pokazać dowód stosowny do zadania.
7. **Panel:** aplikacja pokazuje postęp, historię kroków, wyniki narzędzi, plany oczekujące na zgodę i kroki oczekujące na użytkownika. Awaryjne zatrzymanie pozostaje dostępne.
8. **Pomoc przy dostępie:** Jarvis może otworzyć publiczną stronę HTTPS i poprosić Sebastiana o samodzielne logowanie. Nie przyjmuje haseł na czacie i nie twierdzi, że samo logowanie daje mu dostęp do API.

## Granice, których nie należy ukrywać

- Zatwierdzenie obejmuje wymienione umiejętności i tekstowy zakres planu; nie istnieją jeszcze osobne limity dla każdej wiadomości, adresata, kwoty ani konkretnego pola formularza.
- Uruchamiane programy nie są odizolowane przez pełny sandbox systemu Windows. Uruchomienie wymaga zatwierdzonego planu; nadal należy traktować je jako kod działający na komputerze Sebastiana.
- Nie ma jeszcze uniwersalnego połączenia OAuth/API z dowolnym serwisem, wysyłania e-maili ani publikacji w sklepach czy mediach społecznościowych. Potrzebny jest odpowiedni, konkretny konektor i uprawnienia.
- Historia postępu potwierdza wynik narzędzia, ale nie robi automatycznie zrzutów ekranu ani niezależnej weryfikacji każdej publikacji w zewnętrznej usłudze.
- Pamięć używa lokalnego dopasowania słów, nie rozumie jeszcze niezawodnie relacji semantycznych między dowolnymi projektami.
- W tej zmianie sprawdzono składnię plików Pythona. Nie uruchamiano zestawu testów ani prawdziwych integracji.


## Fundament autonomii eksperckiej — 2026-10-31

- `agent/mission_runtime.py` — trwały graf misji w SQLite: kroki, zależności, statusy, retry, dowody i zdarzenia.
- `skills/mission_manager.py` — API tworzenia, wznawiania, pauzowania i zatrzymywania misji.
- `skills/vision.py` — świeże screenshoty, metadane, hash i opcjonalny OCR.
- `skills/computer_operator.py` — kontrolowane ręce Windows, blokowane bez zatwierdzonej misji.
- `skills/independent_verifier.py` — deterministyczne dowody plików, tekstu, wartości i SHA-256.
- `skills/mission_recovery.py` — bounded recovery po błędach.
- `skills/skill_acquisition.py` — analiza AST kandydata bez uruchamiania obcego kodu.
- `skills/memory_manager.py` — lokalne kategorie pamięci użytkownika, epizodów, procedur i wiedzy.
- `skills/background_tasks.py` + `agent/background_worker.py` — zatwierdzane harmonogramy i worker z limitami.
- `agent/model_router.py` — profile wyboru skonfigurowanego modelu: general, fast, code, vision, private.
- `agent/agent_gui.py` — Centrum zadań pokazuje także trwałe misje i postęp kroków.

Te funkcje są zaimplementowane i przetestowane deterministycznie. Nie oznacza to automatycznego dostępu do dowolnych usług zewnętrznych ani obejścia logowania, CAPTCHA, 2FA lub wymaganych zgód.
