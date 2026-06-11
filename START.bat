@echo off
REM ===== Authentication Quick Start Script =====
REM This script automates the setup and running of Authentication

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║       Authentication - Multi-Factor Authentication       ║
echo ║              Quick Start Script                    ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo    Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
    echo.
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.

REM Install dependencies
echo 📥 Installing dependencies...
echo    This may take a few minutes on first run...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    echo    Try: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

REM Check MongoDB
echo 🗄️  Checking MongoDB...
mongod --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  WARNING: MongoDB not found in system PATH
    echo    Make sure MongoDB is installed and running!
    echo.
    echo    To start MongoDB manually:
    echo    - Windows: Open Services, find MongoDB, and start it
    echo    - Or run: net start MongoDB
    echo.
) else (
    echo ✓ MongoDB found
    echo.
)

REM Display startup instructions
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║              Pre-Startup Checklist                 ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo ☐ 1. MongoDB is running (check Services or run 'net start MongoDB')
echo ☐ 2. Port 5000 is available (not used by other apps)
echo ☐ 3. Webcam is connected (for face authentication)
echo.

REM Ask user to start MongoDB
set /p mongodb=Is MongoDB running? (yes/no): 
if /i not "%mongodb%"=="yes" (
    echo.
    echo To start MongoDB on Windows:
    echo 1. Press Win+R
    echo 2. Type 'services.msc' and press Enter
    echo 3. Find 'MongoDB' in the list
    echo 4. Right-click and select 'Start'
    echo.
    pause
    exit /b 1
)

REM Start Flask application
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║          Starting Authentication Application            ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo 🚀 Starting Flask server...
echo.
echo    Server will be running at: http://127.0.0.1:5000
echo.
echo    Press CTRL+C to stop the server
echo.

REM Run the application
python app.py

REM If app stops, ask if user wants to do anything else
echo.
echo Server stopped.
pause
