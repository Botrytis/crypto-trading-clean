@echo off
REM Start Streamlit Web UI (Windows)

echo.
echo ========================================
echo  Starting Crypto Trading Web UI...
echo ========================================
echo.
echo UI will be available at: http://localhost:8501
echo.
echo WARNING: Make sure API is running first!
echo    Run: scripts\start_api.bat (in another terminal)
echo.

cd /d "%~dp0\.."

REM Activate venv if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start Streamlit
streamlit run src\crypto_trader\web\app.py
