@echo off
chcp 65001 >nul
setlocal

echo ========================================================
echo  Installerar ESG AI Tool (Gemini CLI)
echo ========================================================
echo.

:: 1. Kontrollera om Python finns
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEL] Python hittades inte på din dator.
    echo.
    echo Vi öppnar nu webbläsaren så du kan ladda ner Python.
    echo Vänligen installera det och se till att kryssa i "Add Python to PATH".
    echo.
    timeout /t 3 >nul
    start https://www.python.org/downloads/
    echo När du har installerat Python, kör denna fil igen.
    pause
    exit /b
)

:: 2. Skapa virtuell miljö (för att inte påverka andra program)
echo [INFO] Skapar isolerad miljö (.venv)...
if not exist ".venv" (
    python -m venv .venv
) else (
    echo .venv finns redan, fortsätter...
)

:: 3. Uppdatera pip och installera verktyget
echo [INFO] Installerar verktyget och nödvändiga bibliotek...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install .

echo.
echo ========================================================
echo  Installation klar!
echo ========================================================
echo.
echo Du kan nu använda "start.bat" för att köra verktyget.
echo.
echo OBS: Första gången du kör verktyget kommer du behöva ange
echo en API-nyckel om du vill använda AI-funktionerna.
echo.
pause
