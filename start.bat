@echo off
REM Quick start script for Earning Robot (Windows)

echo 🤖 Earning Robot - Quick Start
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your API keys before continuing!
    echo    Required: TELEGRAM_BOT_TOKEN, TELEGRAM_OWNER_ID
    echo.
    pause
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt --quiet

REM Create data directory
if not exist data mkdir data
if not exist logs mkdir logs

echo.
echo ✅ Setup complete!
echo.
echo 🚀 Starting Earning Robot...
echo ================================
echo.

REM Run the robot
python main.py
