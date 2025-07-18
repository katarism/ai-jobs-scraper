# AI Jobs Japan Scraper

A real web scraper that automatically finds and collects AI/ML job opportunities in Japan from multiple sources and stores them in a Notion database.

## Features

- **Real-time scraping** from multiple job sources:
  - LinkedIn Jobs
  - Indeed Japan
  - Mercari Careers
  - Rakuten Careers
  - LINE Careers
  - Google Careers
  - Amazon Careers

- **AI/ML job filtering** using comprehensive keyword matching
- **Duplicate detection** to avoid adding the same job twice
- **Automatic Notion integration** for job storage and tracking
- **Rate limiting** to be respectful to job sites
- **Robust error handling** for reliable operation

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with your Notion credentials:
   ```
   NOTION_TOKEN=your_notion_integration_token
   AI_JOBS_DATABASE_ID=your_jobs_database_id
   CHANGE_LOG_DATABASE_ID=your_changelog_database_id
   ```

3. **Configure job sources:**
   Edit `config.py` to enable/disable job sources or modify search terms.

## Usage

### Run the full scraper:
```bash
python scraper.py
```

### Test the scraper (recommended first):
```bash
python test_scraper.py
```

## How it works

1. **Web Scraping**: Uses Selenium WebDriver to navigate job sites and extract job information
2. **Data Extraction**: Parses job titles, companies, locations, and URLs from job listings
3. **AI Filtering**: Uses keyword matching to identify AI/ML related positions
4. **Duplicate Check**: Verifies jobs don't already exist in your Notion database
5. **Notion Storage**: Creates structured job entries in your Notion database
6. **Activity Logging**: Records scraping activities for monitoring

## Job Sources

The scraper targets these major job platforms and company career sites:

- **LinkedIn**: Searches for AI/ML positions in Japan
- **Indeed Japan**: Japanese job board with AI/ML listings
- **Company Careers**: Direct scraping from major tech companies in Japan

## Configuration

Edit `config.py` to customize:

- **Search terms**: Modify AI/ML keywords for job searches
- **Rate limits**: Adjust delays between requests
- **Job limits**: Set maximum jobs per source
- **Chrome options**: Configure browser behavior

## Notion Database Schema

The scraper expects a Notion database with these fields:
- Job Title (title)
- Company (select)
- Location (rich_text)
- Job Link (url)
- Description (rich_text)
- Data Source (select)
- AI Relevance Level (select)
- Newsletter Status (select)
- Position Type (select)
- Date Added (date)
- Date Last Checked (date)
- Status (select)

## Troubleshooting

- **Chrome driver issues**: The scraper automatically downloads the correct ChromeDriver version
- **Rate limiting**: Increase `REQUEST_DELAY` in config.py if you encounter blocking
- **Selector changes**: Job sites may update their HTML structure; check selectors in the code
- **Notion API limits**: The scraper includes built-in rate limiting for Notion API calls

## Legal and Ethical Considerations

- **Respect robots.txt**: The scraper follows website terms of service
- **Rate limiting**: Built-in delays prevent overwhelming job sites
- **Data usage**: Only collects publicly available job information
- **Terms of service**: Review and comply with each job site's terms

## Support

For issues or questions:
1. Check the error logs in the console output
2. Verify your Notion credentials and database setup
3. Test with the `test_scraper.py` script first
4. Review the configuration in `config.py`
