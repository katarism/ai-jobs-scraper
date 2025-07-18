# AI Jobs Scraper - Cleaned Codebase Structure

## 📂 Core Application Files

### **Main Application**
- **`scraper.py`** - Main scraper with auto-detection logic and intelligent strategy selection
- **`gui_controller.py`** - GUI application for managing job sources with auto-analysis features
- **`website_analyzer.py`** - Smart website analysis for optimal scraping strategy detection
- **`config.py`** - Configuration file with job sources and settings

### **Supporting Modules**
- **`notion_client.py`** - Notion database integration for storing scraped jobs
- **`rate_limiter.py`** - Rate limiting functionality for responsible scraping

## 🧪 Testing
- **`test_website_analyzer.py`** - Comprehensive tests for the website analyzer (23 test cases)

## 📋 Configuration & Setup
- **`requirements.txt`** - Python dependencies list
- **`setup_env.sh`** - Automated virtual environment setup script
- **`run_gui.sh`** - GUI launcher script with automatic environment detection

## 📚 Documentation
- **`README.md`** - Main project documentation
- **`GUI_USAGE.md`** - Detailed GUI usage guide
- **`CODEBASE_STRUCTURE.md`** - This file (codebase overview)
- **`commands.txt`** - Commands reference (preserved as requested)

## 🗑️ Removed Files (Cleanup)

The following unused/development files were removed:
- `scraper_enhanced.py` - Alternative scraper implementation (unused)
- `scraper_focused.py` - Alternative scraper implementation (unused)
- `test_enhanced.py` - Tests for unused enhanced scraper
- `test_focused.py` - Tests for unused focused scraper
- `test_scraper.py` - Basic scraper tests (replaced by website analyzer tests)
- `debug_test.py` - Development/debug file

## 🚀 Quick Start Commands

### Run GUI
```bash
python3.13 gui_controller.py
# or
./run_gui.sh
```

### Run Tests
```bash
python3.13 test_website_analyzer.py
```

### Setup Environment
```bash
./setup_env.sh
```

## 🏗️ Architecture Overview

### **Auto Scraping Type System**
1. **WebsiteAnalyzer** analyzes target websites
2. **Strategy Selection** chooses optimal method (API/Requests/Selenium)
3. **Fallback System** ensures reliability with graceful degradation
4. **Confidence Scoring** provides transparency in decision-making

### **GUI Features**
- **Smart Defaults** - Auto scraping type as default
- **Real-time Analysis** - Test Analysis button for immediate feedback
- **Graceful Degradation** - Works even without analysis dependencies
- **Visual Feedback** - Clear indicators for available features

### **Core Scraping Logic**
- **Dynamic Strategy Selection** per source
- **Caching** of analysis results for performance
- **Multiple Fallback Layers** for maximum reliability
- **Generic Scraping Support** for new unknown sources

## 📊 Dependencies

### **Core Dependencies**
- `requests` - HTTP client for API and simple scraping
- `beautifulsoup4` - HTML parsing for requests-based scraping
- `selenium` - Browser automation for complex sites
- `python-dotenv` - Environment variable management
- `webdriver-manager` - Automatic WebDriver management

### **GUI Dependencies**
- `tkinter` - GUI framework (comes with Python)

## 🔧 Configuration

All job sources are configured in `config.py` with support for:
- **Manual Type Selection** - `selenium`, `api`, `requests`
- **Auto Detection** - `auto` (uses WebsiteAnalyzer)
- **Flexible URL Patterns** - Support for both direct URLs and search patterns
- **Enable/Disable** - Individual source control

## ✅ Quality Assurance

- **23 Comprehensive Tests** covering all analyzer functionality
- **Error Handling** with graceful degradation
- **Dependency Checking** with helpful error messages
- **Clean Code Structure** with separation of concerns
- **Documentation** for all major components