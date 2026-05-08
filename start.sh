#!/bin/bash

# ===== AuthSafe Quick Start Script =====
# This script automates the setup and running of AuthSafe

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║       AuthSafe - Multi-Factor Authentication       ║"
echo "║              Quick Start Script                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 not found!"
    echo "   Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to activate virtual environment"
    exit 1
fi
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
echo "   This may take a few minutes on first run..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to install dependencies"
    echo "   Try: pip install -r requirements.txt"
    exit 1
fi
echo "✓ Dependencies installed"
echo ""

# Check MongoDB
echo "🗄️  Checking MongoDB..."
if ! command -v mongod &> /dev/null; then
    echo "⚠️  WARNING: MongoDB not found"
    echo "   Make sure MongoDB is installed and running!"
    echo ""
    echo "   To install MongoDB:"
    echo "   - macOS: brew install mongodb-community"
    echo "   - Ubuntu: sudo apt install mongodb"
    echo ""
    echo "   To start MongoDB:"
    echo "   - macOS: brew services start mongodb-community"
    echo "   - Ubuntu: sudo systemctl start mongod"
    echo ""
else
    echo "✓ MongoDB found"
    echo ""
fi

# Display startup instructions
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║              Pre-Startup Checklist                 ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "☐ 1. MongoDB is running"
echo "☐ 2. Port 5000 is available"
echo "☐ 3. Webcam is connected"
echo ""

# Ask user to confirm MongoDB is running
read -p "Is MongoDB running? (yes/no): " mongodb_running
if [ "$mongodb_running" != "yes" ]; then
    echo ""
    echo "To start MongoDB:"
    echo "  macOS: brew services start mongodb-community"
    echo "  Ubuntu: sudo systemctl start mongod"
    echo ""
    exit 1
fi

# Start Flask application
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║          Starting AuthSafe Application            ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Starting Flask server..."
echo ""
echo "   Server will be running at: http://127.0.0.1:5000"
echo ""
echo "   Press CTRL+C to stop the server"
echo ""

# Run the application
python app.py
