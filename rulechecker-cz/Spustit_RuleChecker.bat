@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
)

echo ==============================================
echo   RuleChecker CZ/EN - spousteni
echo ==============================================
echo.
echo Pouzity interpreter: %PYTHON_EXE%
echo.

%PYTHON_EXE% main.py
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo Hotovo. Vystupni soubory byly vygenerovany.
) else (
    echo Spusteni skoncilo s chybou (kod %EXIT_CODE%).
    echo Zkontrolujte, ze mate nainstalovane zavislosti:
    echo   pip install -r requirements.txt
)
echo.
pause
exit /b %EXIT_CODE%
