@echo off
chcp 65001 >nul
setlocal

:: Kontrollera att installationen är gjord
if not exist ".venv" (
    echo [FEL] Ingen installation hittades. Kör "install.bat" först.
    pause
    exit /b
)

:: Aktivera miljön
call .venv\Scripts\activate.bat

:: Rensa skärmen och visa välkomstmeddelande
cls
echo ========================================================
echo  ESG AI Tool
echo ========================================================
echo.

:: Starta chatten direkt
python -m gemini_cli.main chat

:: Om programmet avslutas (hon skriver exit), pausa så fönstret inte bara försvinner
echo.
echo Avslutar...
pause
