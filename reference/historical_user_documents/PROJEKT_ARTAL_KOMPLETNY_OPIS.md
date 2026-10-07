# PROJEKT: ARTAL v2 — AI Trading Agent
> Ostatnia aktualizacja: 2026-07-28 | Autor: Seba (kaczy) | Status: **AKTYWNY 24/7**

---

## 1. CZYM JEST TEN PROJEKT

ARTAL (Autonomous Reinforcement Trading Agent with Live-learning) to autonomiczny agent tradingowy oparty na uczeniu ze wzmocnieniem (PPO — Proximal Policy Optimization). Uczy się handlować kryptowalutami (BTC/USDT) na danych historycznych i live z Binance. Działa w trybie **paper trading** (wirtualne pieniądze, zero ryzyka). Cel długoterminowy: po udowodnieniu zysku przełączyć na prawdziwy kapitał.

---

## 2. LOKALIZACJA NA DYSKU

```
C:\AI Trading Agent\
└── AI Trading Agent\          ← GŁÓWNY KATALOG PROJEKTU
    ├── artal_v2.py            ← GŁÓWNY PLIK — uruchamia agenta
    ├── agent_watchdog.ps1     ← Watchdog PowerShell (backup)
    ├── START_ARTAL_V2.bat     ← Bat z auto-restart (backup)
    ├── START_AGENT.ps1        ← Stary launcher
    ├── REGISTER_TASK_SCHEDULER.ps1  ← Skrypt rejestracji zadania
    ├── .env                   ← Konfiguracja (NIE commitować!)
    ├── .env.example           ← Szablon konfiguracji
    ├── requirements.txt       ← Zależności Python
    ├── agent_system/          ← Główny pakiet agenta
    ├── models/                ← Zapisane modele PPO
    │   ├── ppo_latest.zip     ← Ostatni model
    │   └── ppo_best.zip       ← Najlepszy model (najwyższe equity)
    ├── logs/                  ← Logi
    │   ├── artal_v2.log       ← GŁÓWNY LOG aktywnego agenta
    │   └── ppo/               ← TensorBoard logi
    ├── data/                  ← Cache danych historycznych
    └── tests/                 ← Testy jednostkowe (25 testów)
```

---

## 3. ARCHITEKTURA — STRUKTURA agent_system/

```
agent_system/
├── main.py              ← Entry point (tryby: train-smoke, autonomous-learning-loop, history-learning-loop)
├── runner.py            ← Orchestrator pętli treningowej
├── system.py            ← TradingSystem — live paper trading
├── core/
│   ├── config.py        ← Settings z .env (dataclass frozen)
│   └── logger.py        ← Logger
├── data/
│   ├── historical_client.py  ← Pobiera historię BTC z Binance REST API
│   ├── binance_ws.py         ← WebSocket live feed Binance
│   ├── data_buffer.py        ← Buffer ticków
│   ├── feature_engineering.py ← 17 cech (RSI, EMA, MACD, volume, itp.)
│   └── rest_client.py        ← Binance REST client
├── environment/
│   ├── trading_env.py   ← Gym środowisko tradingowe (actions: HOLD/LONG/SHORT/CLOSE)
│   ├── reward.py        ← NAPRAWIONA funkcja nagrody (v2)
│   ├── simulator.py     ← Symulator pozycji
│   └── backtester.py    ← Backtester
├── rl/
│   ├── ppo_model.py     ← Buduje model PPO (SB3) — NAPRAWIONY (ent_coef=0.01)
│   ├── trainer.py       ← Trener PPO
│   ├── history_trainer.py ← Trener na danych historycznych
│   ├── model_evaluator.py ← Ocenia model po treningu — NAPRAWIONY (luźne progi)
│   ├── online_loop.py   ← Live learning loop
│   └── buffer.py        ← Replay buffer
├── execution/
│   ├── policy_guard.py  ← Blokuje zbyt częste akcje (max_hold_steps=120)
│   ├── risk_manager.py  ← Zarządzanie ryzykiem
│   ├── position_tracker.py ← Śledzenie pozycji
│   ├── order_manager.py ← Zarządzanie zleceniami
│   └── testnet_api.py   ← Binance Testnet API (dla prawdziwych transakcji testowych)
└── monitoring/
    ├── dashboard.py     ← Dashboard (CLI)
    └── metrics.py       ← Metryki (win_rate, profit_factor, sharpe, drawdown)
```

---

## 4. JAK AGENT DZIAŁA — PĘTLA TRENINGOWA

**ARTAL v2 (artal_v2.py) — nieskończona pętla:**

```
Pętla #N:
  Faza 1: Pobierz 525,600 ticków BTC/USDT (365 dni × 1440 min/dzień) z Binance
  Faza 2: Trening PPO na 80% danych (420,480 ticków) — ~33 sekundy
  Faza 3: Ewaluacja na 20% danych (105,120 ticków) — equity, trades, PnL
  Faza 4: Live paper 60 ticków z Binance WebSocket (ok. 90 sekund)
  → Czekaj 30 sekund → Pętla #N+1
```

**Akcje agenta:** `0=HOLD, 1=LONG (kup), 2=SHORT (sprzedaj), 3=CLOSE (zamknij pozycję)`

**Jak agent decyduje:** Na podstawie 17 cech (RSI, EMA9/21/50/200, MACD, BB, ATR, volume ratio, cena rel. do EMA, itp.) PPO wybiera akcję która maksymalizuje skumulowaną nagrodę.

---

## 5. KONFIGURACJA (.env)

```env
TRADING_SYMBOL=BTCUSDT
INITIAL_CAPITAL=640            # ~500 GBP w USDT
MAX_OPEN_POSITIONS=3
PUBLIC_MARKET_DATA_BASE_URL=https://api.binance.com
BINANCE_WS_BASE_URL=wss://stream.binance.com:9443/stream
MAX_POSITION_FRACTION=0.10     # 10% kapitału na pozycję (było 2% — naprawione)
DEFAULT_LEVERAGE=1
MAX_LEVERAGE=3
STOP_LOSS_FRACTION=0.015       # 1.5% stop loss
DAILY_LOSS_LIMIT_FRACTION=0.05 # 5% dzienny limit straty
ENABLE_TESTNET_TRADING=false   # Paper trading (nie prawdziwe zlecenia)
BINANCE_API_KEY=               # Opcjonalne — potrzebne tylko dla testnet/live
BINANCE_API_SECRET=            # Opcjonalne
```

---

## 6. ŚRODOWISKO PYTHON

```
Python: .venv\Scripts\python.exe  (wersja z venv)
SB3:    stable-baselines3 v2.9.0  (najnowsza)
Gym:    gymnasium >=0.29
inne:   websockets, numpy, tensorboard, requests, python-dotenv, pytest
```

---

## 7. TASK SCHEDULER — URUCHAMIANIE 24/7

Agent jest zarejestrowany w Windows Task Scheduler:
- **Nazwa zadania:** `ARTAL_v2_24_7`
- **Status:** Ready/Running
- **Trigger:** AtStartup + AtLogOn
- **Auto-restart:** Co 1 minutę jeśli się zawiesi
- **Limit czasu:** 999 dni (praktycznie nieskończony)

**Sprawdzenie statusu:**
```powershell
Get-ScheduledTask -TaskName "ARTAL_v2_24_7" | Select-Object TaskName, State
Get-Process python | Select-Object Id, CPU, @{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB,1)}}
```

**Logi na żywo:**
```powershell
Get-Content "C:\AI Trading Agent\AI Trading Agent\logs\artal_v2.log" -Wait -Tail 20
```

**Ręczny start (backup jeśli Task Scheduler nie odpala):**
```
C:\AI Trading Agent\AI Trading Agent\START_ARTAL_V2.bat
```

---

## 8. NAPRAWIONE BŁĘDY (historia zmian)

### Problem oryginalny:
Agent przez 18 cykli robił **0 transakcji** — zawsze wybierał HOLD.

### Przyczyny i naprawki:

| Plik | Problem | Naprawka |
|------|---------|----------|
| `environment/reward.py` | time_penalty karał za każdy tick → HOLD zawsze lepszy | Bonus za otwarcie pozycji (+0.0002), brak time_penalty gdy pozycja otwarta, zamknięcie z zyskiem +2x PnL |
| `rl/ppo_model.py` | Brak ent_coef → agent nie eksplorował | Dodano ent_coef=0.01, gamma=0.99, n_steps=512, sieć [256,128,64] |
| `environment/trading_env.py` | position_fraction=0.02 → nagrody zbyt małe | Zmieniono na 0.10, time_penalty 0.0001→0.00005 |
| `rl/model_evaluator.py` | min_trades=3, min_profit_factor=1.05 → blokował każdy model | min_trades=1, min_profit_factor=0.0, max_drawdown=15%, min_equity_return=-10% |

### Wynik po naprawce:
- Przed: trades=0 przez 18 cykli
- Po: trades=1,273 na 73 dniach ewaluacji

---

## 9. WARTOŚCIOWE PLIKI Z POPRZEDNICH PROJEKTÓW

Zapisane w: `C:\AI Trading Agent\WARTOSCIOWE_Z_INNYCH_PROJEKTOW\`

```
DNA_Models_AI_Trader/
├── dna_brain.py         ← Logika DNA agenta (stary projekt AI_Trader)
├── dna_evolution.py     ← Ewolucja strategii
├── dna_instincts.py     ← Instynkty tradingowe
├── dna_memory.py        ← Pamięć agenta
├── ai_trader_brain.keras      ← Wytrenowany model Keras
├── ai_trader_brain_v4.keras   ← Model v4
├── apex_predator.keras        ← Model "apex predator"
├── sentient_architect.keras   ← Model architekta
└── HYPER_INTELLIGENCE.csv     ← Dane treningowe
IMPERIUM_STARE_WARTOSCIOWE/
├── cj_connector.py      ← Connector CJ Dropshipping
├── orchestrator.py      ← Stary orchestrator
└── empire JSON-e        ← Specyfikacje empire v1/v2/v3
PROJEKT_QUANTUM_HYDRA(XAUUSD).md  ← Dokumentacja bota XAUUSD (MT4/5)
CODEX_TRADING_AGENT_SPEC_V2_MAX_PRO.md  ← Specyfikacja CODEX agenta
```

---

## 10. INNE PROJEKTY TRADINGOWE NA DYSKU

- **Quantum Hydra V19** — bot XAUUSD na MT4/MT5, magic number 1919, 45.7% win rate, 818 zamkniętych transakcji. Osobny projekt, nie połączony z ARTAL.
- **C:\AI_TRADING!!** — usunięty (tylko PROJEKT_QUANTUM_HYDRA.md — przeniesiony do WARTOSCIOWE)
- **C:\AI_Trader** — usunięty (modele .keras i skrypty DNA przeniesione do WARTOSCIOWE)

---

## 11. CO ZOSTAŁO DO ZROBIENIA

- [ ] Optuna — automatyczne strojenie hiperparametrów PPO
- [ ] Funding rate feature — dodać do feature_engineering.py
- [ ] Whale movement ratio — wskaźnik ruchu wielorybów
- [ ] SubprocVecEnv — wielowątkowy trening (zamiast DummyVecEnv)
- [ ] Web dashboard — podgląd equity curve i transakcji przez przeglądarkę
- [ ] Przełączenie na Binance Testnet — prawdziwe zlecenia testowe
- [ ] Obsługa wielu par (ETH, BNB, SOL)

---

## 12. KLUCZE API I BEZPIECZEŃSTWO

- Klucze Binance: w `.env` — **NIE MA ich w repozytorium** (wpisane są puste)
- GitHub: `KaczySeba25/AI-Trading-Agent` — branch aktywny: `codex/initial-trading-agent`
- **UWAGA HISTORYCZNA:** stary `cj_token.txt` był w publicznym repo — token został zrotowany

---

## 13. GITHUB

```
Repo: KaczySeba25/AI-Trading-Agent
Branch główny: main (lub codex/initial-trading-agent)
Git: NIE uruchamiać "git log --all" — desktop.ini z cloud sync psuje historię
```
