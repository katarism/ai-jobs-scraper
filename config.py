import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Notion Configuration
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
AI_JOBS_DATABASE_ID = os.getenv('AI_JOBS_DATABASE_ID')
CHANGE_LOG_DATABASE_ID = os.getenv('CHANGE_LOG_DATABASE_ID')

# API Configuration
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Rate Limiting
REQUEST_DELAY = 1  # seconds between requests
MAX_RETRIES = 3

# Scraping Configuration
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# Job Sources
JOB_SOURCES = {
    'openai': {
        'name': 'OpenAI',
        'api_url': 'https://api.openai.com/v1/jobs',
        'enabled': True
    },
    'xai': {
        'name': 'xAI',
        'api_url': 'https://xai.com/careers/api/jobs',
        'enabled': True
    },
    'mercari': {
        'name': 'Mercari',
        'url': 'https://careers.mercari.com/job-category/engineering-design/',
        'enabled': True,
        'type': 'selenium'
    }
}

# Chrome Options for Selenium
CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    f"--user-agent={USER_AGENT}"
]

# Validation
if not all([NOTION_TOKEN, AI_JOBS_DATABASE_ID, CHANGE_LOG_DATABASE_ID]):
    print("⚠️  Warning: Missing required environment variables")
    print(f"NOTION_TOKEN: {'✅' if NOTION_TOKEN else '❌'}")
    print(f"AI_JOBS_DATABASE_ID: {'✅' if AI_JOBS_DATABASE_ID else '❌'}")
    print(f"CHANGE_LOG_DATABASE_ID: {'✅' if CHANGE_LOG_DATABASE_ID else '❌'}")