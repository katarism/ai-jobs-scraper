# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Scraper
```bash
# Run the full AI jobs scraper
python scraper.py

# Test the scraper (recommended first)
python test_scraper.py

# Run the GUI controller for managing job sources
python gui_controller.py
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables (create .env file)
NOTION_TOKEN=your_notion_integration_token
AI_JOBS_DATABASE_ID=your_jobs_database_id
CHANGE_LOG_DATABASE_ID=your_changelog_database_id
```

### Testing Individual Components
```bash
# Test individual scraper components
python test_enhanced.py
python test_focused.py

# Test website analyzer (if available)
python website_analyzer.py

# Debug Notion connection
python debug_test.py
```

## Architecture Overview

### Core Components

**Scraper Engine (`scraper.py`)**
- Main `AIJobsScraper` class with adaptive scraping strategies
- Auto-detects optimal scraping method (API, requests, or Selenium) using `WebsiteAnalyzer`
- Supports multiple job sources with different extraction methods
- Built-in rate limiting and error handling

**Configuration Management (`config.py`)**
- `JOB_SOURCES` dictionary defines all job sources with their settings
- Each source can have: `name`, `enabled`, `url`, `type`, `base_url`, `search_terms`
- Supported types: `'auto'` (AI-detected), `'selenium'`, `'api'`, `'requests'`
- AI keyword filtering via `AI_KEYWORDS` list

**Notion Integration (`notion_client.py`)**
- `NotionClient` class handles all Notion database operations
- Automatic duplicate detection via `check_job_exists()`
- Structured job entry creation with proper field typing
- Activity logging to change log database

**Website Analysis (`website_analyzer.py`)**
- `WebsiteAnalyzer` automatically determines best scraping strategy
- Detects API endpoints, JavaScript dependency, SPA patterns, anti-bot measures
- Returns confidence scores and strategy recommendations
- Used when scraping type is set to `'auto'`

**GUI Controller (`gui_controller.py`)**
- Tkinter-based interface for managing job sources without editing code
- Load/save configuration to `config.py`
- Add/edit/delete companies with career page URLs
- Enable/disable scraping per company
- Test URLs and website analysis integration

### Scraping Strategies

The scraper automatically selects the best approach for each source:

1. **API Strategy**: Direct JSON endpoint access (fastest, most reliable)
2. **Requests Strategy**: HTTP requests + BeautifulSoup parsing (efficient for simple sites)
3. **Selenium Strategy**: Browser automation (fallback for complex JavaScript sites)

### Data Flow

1. **Configuration Loading**: `JOB_SOURCES` from `config.py`
2. **Strategy Selection**: `WebsiteAnalyzer` determines optimal approach per source
3. **Data Extraction**: Source-specific extractors parse job data
4. **AI Filtering**: Keywords filter for AI/ML relevance
5. **Duplicate Check**: Notion database query to avoid duplicates
6. **Storage**: Structured job entries created in Notion

### Job Source Configuration

Each source in `JOB_SOURCES` supports:
- `name`: Display name
- `enabled`: Boolean to enable/disable scraping
- `url`: Direct career page URL
- `base_url`: Search base URL (for job boards)
- `search_terms`: Array of search keywords (for job boards)
- `type`: `'auto'`, `'selenium'`, `'api'`, or `'requests'`

### CI/CD Integration

GitHub Actions workflow (`.github/workflows/scrape.yml`):
- Runs twice daily (JST 9:00 and 21:00)
- Automated Chrome/ChromeDriver setup
- Secrets for Notion API credentials
- Artifact upload for debugging

## Extending the Scraper

### Adding New Job Sources

1. **Via GUI**: Use `gui_controller.py` to add sources graphically
2. **Via Code**: Add entries to `JOB_SOURCES` in `config.py`

For complex sites requiring custom logic, add extraction methods following the pattern:
- `_scrape_[source]_jobs()` for main scraping logic
- `_extract_[source]_job()` for individual job data extraction

### Notion Database Schema

Expected fields in the jobs database:
- Job Title (title)
- Company (select)
- Location (rich_text)
- Job Link (url)
- Description (rich_text)
- Data Source (select)
- AI Relevance Level (select): High/Medium/Low/Unknown
- Newsletter Status (select)
- Position Type (select)
- Date Added (date)
- Date Last Checked (date)
- Status (select)

### Rate Limiting and Ethics

- Built-in `REQUEST_DELAY` between requests (configurable in `config.py`)
- Respects robots.txt and website terms of service
- User-Agent rotation and reasonable request patterns
- Automatic backoff on rate limiting responses