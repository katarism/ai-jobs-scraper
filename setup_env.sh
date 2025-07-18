#!/bin/bash

# AI Jobs Scraper - Environment Setup Script
# This script sets up a proper virtual environment for the application

set -e  # Exit on any error

echo "🚀 Setting up AI Jobs Scraper environment..."

# Check if we're in the right directory
if [ ! -f "gui_controller.py" ]; then
    echo "❌ Error: Please run this script from the AI Jobs Scraper directory"
    exit 1
fi

# Create virtual environment with Python 3.13
echo "📦 Creating virtual environment..."
python3.13 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Fallback: install essential packages
    pip install requests beautifulsoup4 selenium python-dotenv webdriver-manager
fi

echo "✅ Environment setup complete!"
echo ""
echo "🎯 To use the environment:"
echo "   source venv/bin/activate"
echo "   python gui_controller.py"
echo ""
echo "🔧 To run the GUI directly:"
echo "   ./run_gui.sh"