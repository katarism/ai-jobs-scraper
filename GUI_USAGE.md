# AI Jobs Scraper - GUI Usage Guide

## 🚀 Quick Start

### Option 1: Direct Run (Recommended)
```bash
cd "/Users/cherylwhoo/Documents/PJ-AI Jobs in Japan/AI Jobs Scraper"
python3.13 gui_controller.py
```

### Option 2: Using Launch Script
```bash
cd "/Users/cherylwhoo/Documents/PJ-AI Jobs in Japan/AI Jobs Scraper"
./run_gui.sh
```

### Option 3: Virtual Environment Setup
```bash
cd "/Users/cherylwhoo/Documents/PJ-AI Jobs in Japan/AI Jobs Scraper"
./setup_env.sh
source venv/bin/activate
python gui_controller.py
```

## 🔧 Troubleshooting

### Error: ModuleNotFoundError: No module named 'requests'

**Solution 1 - Quick Fix:**
```bash
python3.13 -m pip install --break-system-packages requests beautifulsoup4
```

**Solution 2 - Virtual Environment (Recommended):**
```bash
python3.13 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4
python gui_controller.py
```

**Solution 3 - Use System Python:**
```bash
/usr/bin/python3 gui_controller.py
```

### Error: ModuleNotFoundError: No module named '_tkinter'

**Solution:**
```bash
brew install python-tk
```

## 🎯 GUI Features

### 🆕 Auto Scraping Type
- **Smart Analysis**: Automatically detects the best scraping method for each website
- **Confidence Scoring**: Shows how confident the system is in its recommendation
- **Fallback Safety**: Falls back to Selenium if analysis fails

### 🔍 Test Analysis Button
- **Real-time Analysis**: Test websites before adding them to your sources
- **Detailed Results**: See API detection, JavaScript complexity, and anti-bot measures
- **Strategy Explanation**: Understand why a particular method was recommended

### 📊 Analysis Results Display
Shows detailed information about each website:
- **Strategy**: Recommended scraping method (API/Requests/Selenium)
- **Confidence**: How sure the system is about the recommendation
- **Technical Details**: API detection, JavaScript complexity, SPA detection, etc.
- **Response Time**: How fast the website responds

## 🎛️ Scraping Types

### 🤖 Auto (Recommended)
- Automatically analyzes website and selects optimal method
- **Best for**: New sources where you're unsure of the optimal approach
- **Fallback**: Uses Selenium if analysis fails

### 🌐 Requests
- Simple HTTP requests with HTML parsing
- **Best for**: Static websites with simple HTML structure
- **Fastest**: Most efficient method when applicable

### 🔌 API
- Direct API endpoint access
- **Best for**: Websites that expose JSON APIs
- **Most Reliable**: Direct data access without parsing

### 🤖 Selenium
- Browser automation with full JavaScript support
- **Best for**: Complex single-page applications (SPAs)
- **Most Compatible**: Works with any website but slower

## 💡 Tips for Best Results

### 🎯 Using Auto Mode
1. Enter the career/jobs page URL (not the main website)
2. Click "Test Analysis" to see the recommendation
3. Review the confidence score and explanation
4. The system will auto-select the best type

### 🔍 Reading Analysis Results
- **Confidence > 80%**: High confidence, recommended strategy should work well
- **Confidence 50-80%**: Medium confidence, may need manual adjustment
- **Confidence < 50%**: Low confidence, consider manual selection

### ⚠️ When Auto Analysis Isn't Available
- The GUI will fall back to manual selection
- "Test Analysis" button will be disabled
- Install dependencies using the setup script or manual installation

## 🛠️ Advanced Usage

### 🔄 Virtual Environment Management
```bash
# Setup new environment
./setup_env.sh

# Activate existing environment
source venv/bin/activate

# Deactivate environment
deactivate
```

### 📝 Adding New Sources
1. **Company Name**: Internal identifier (lowercase, no spaces)
2. **Display Name**: Human-readable name shown in the interface
3. **URL**: Direct link to careers/jobs page
4. **Type**: Select "auto" for intelligent detection
5. **Test Analysis**: Click to preview the optimal strategy

### 💾 Configuration Management
- **Save Configuration**: Writes changes back to config.py
- **Reload Configuration**: Discards unsaved changes and reloads from file
- **Auto-backup**: Changes are saved to config.py when you click Save

## 🚨 Error Handling

### Graceful Degradation
- If website analysis dependencies are missing, the GUI continues to work
- Auto analysis features are disabled with clear indicators
- Manual scraping type selection remains fully functional

### Dependency Installation
- GUI shows helpful error messages with installation commands
- Multiple fallback options for different Python installations
- Clear indicators when features are unavailable

## 📞 Support

If you encounter issues:
1. Check the terminal output for specific error messages
2. Try the troubleshooting steps above
3. Use the setup script for automatic environment configuration
4. Fall back to manual scraping type selection if auto-analysis fails