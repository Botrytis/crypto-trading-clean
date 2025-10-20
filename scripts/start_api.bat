@echo off
REM Start FastAPI Backend Server (Windows)

echo.
echo ========================================
echo  Starting Crypto Trading API...
echo ========================================
echo.
echo API will be available at: http://localhost:8001
echo API Documentation: http://localhost:8001/api/docs
echo.

cd /d "%~dp0\.."

REM Activate venv if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start uvicorn with auto-reload
uvicorn crypto_trader.api.main:app --reload --port 8001 --host 0.0.0.0
