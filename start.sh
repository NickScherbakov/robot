#!/bin/bash
# Quick start script for Earning Robot

echo "🤖 Earning Robot - Quick Start"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys before continuing!"
    echo "   Required: TELEGRAM_BOT_TOKEN, TELEGRAM_OWNER_ID"
    echo ""
    read -p "Press Enter after you've configured .env, or Ctrl+C to exit..."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create data directory
mkdir -p data
mkdir -p logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Earning Robot..."
echo "================================"
echo ""

# Run the robot
python main.py
