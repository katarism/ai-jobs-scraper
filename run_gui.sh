#!/bin/bash

# AI Jobs Scraper - GUI Launcher Script
# This script runs the GUI with proper environment handling

set -e  # Exit on any error

echo "🖥️  Starting AI Jobs Scraper GUI..."

# Check if we're in the right directory
if [ ! -f "gui_controller.py" ]; then
    echo "❌ Error: Please run this script from the AI Jobs Scraper directory"
    exit 1
fi

# Check if virtual environment exists and use it
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "🔄 Using virtual environment..."
    source venv/bin/activate
    python gui_controller.py
elif command -v python3.13 &> /dev/null; then
    echo "🐍 Using python3.13..."
    python3.13 gui_controller.py
elif command -v python3 &> /dev/null; then
    echo "🐍 Using python3..."
    python3 gui_controller.py
else
    echo "❌ Error: No compatible Python installation found"
    echo "Please install Python 3.11+ or run setup_env.sh first"
    exit 1
fi