@echo off
cd /d "%~dp0"
if not exist "agent\venv\Scripts\python.exe" (
    echo Nie znaleziono srodowiska Jarvisa. Sprawdz folder agent\venv.
    pause
    exit /b 1
)
"agent\venv\Scripts\python.exe" "agent\agent_gui.py"
if errorlevel 1 pause
