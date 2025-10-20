@echo off
REM Setup script for Crypto Trading Platform (Windows)
REM Creates virtual environment and installs all dependencies

echo.
echo ========================================
echo  Setting up Crypto Trading Platform
echo ========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12+ from https://www.python.org/
    pause
    exit /b 1
)
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo WARNING: Virtual environment already exists
    set /p response="Remove it and create new? (y/N): "
    if /i "%response%"=="y" (
        rmdir /s /q venv
        echo Removed old virtual environment
    ) else (
        echo Using existing virtual environment
    )
)

if not exist venv (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo pip upgraded
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
echo This may take 5-10 minutes...
pip install -r requirements.txt
echo Dependencies installed
echo.

REM Install package in development mode
echo Installing crypto-trader package in development mode...
pip install -e .
echo Package installed
echo.

REM Verify installation
echo Verifying installation...
python -c "from crypto_trader.api.main import app; print('crypto_trader module imports successfully')"
echo.

REM Success message
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Start the API server (Terminal 1):
echo    scripts\start_api.bat
echo.
echo 3. Start the Web UI (Terminal 2):
echo    scripts\start_web.bat
echo.
echo 4. Open your browser:
echo    http://localhost:8501
echo.
echo Documentation:
echo    - API Docs: http://localhost:8001/api/docs
echo    - README: See README.md
echo    - Phase 1 Report: See PHASE1_COMPLETE.md
echo.
echo ========================================
echo.
pause
