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
REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3

# Scraping Configuration
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# Job Sources Configuration
JOB_SOURCES = {
    'linkedin': {
        'name': 'LinkedIn',
        'enabled': True,
        'base_url': 'https://www.linkedin.com/jobs/search/',
        'search_terms': [
            'AI engineer Japan',
            'Machine Learning Japan',
            'Data Scientist Japan',
            'AI researcher Japan',
            'ML engineer Japan',
            'Deep Learning Japan',
            'NLP engineer Japan',
            'Computer Vision Japan',
        ],
    },
    'indeed': {
        'name': 'Indeed',
        'enabled': True,
        'base_url': 'https://jp.indeed.com/jobs',
        'search_terms': [
            'AI engineer',
            'Machine Learning engineer',
            'Data Scientist',
            'AI researcher',
            'ML engineer',
            'Deep Learning engineer',
            'NLP engineer',
            'Computer Vision engineer',
        ],
    },
    'mercari': {
        'name': 'Mercari',
        'enabled': True,
        'url': 'https://careers.mercari.com/job-category/engineering-design/',
        'type': 'selenium',
    },
    'rakuten': {
        'name': 'Rakuten',
        'enabled': True,
        'url': 'https://rakuten.careers/jobs/',
        'type': 'selenium',
    },
    'line': {
        'name': 'LINE',
        'enabled': True,
        'url': 'https://linecorp.com/ja/career/positions/',
        'type': 'selenium',
    },
    'google': {
        'name': 'Google',
        'enabled': True,
        'url': 'https://careers.google.com/jobs/results/?location=Japan&q=AI%20Machine%20Learning',
        'type': 'selenium',
    },
    'amazon': {
        'name': 'Amazon',
        'enabled': True,
        'url': 'https://www.amazon.jobs/en/search.json?business_category[]=research-science&country_code=JP&normalized_country_code=JP',
        'type': 'api',
    },
}

# AI Keywords for filtering
AI_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
    'neural network', 'data science', 'nlp', 'natural language processing',
    'computer vision', 'robotics', 'algorithm', 'model', 'prediction', 
    'analytics', 'intelligence', 'automation', 'optimization', 'recommendation',
    'chatbot', 'gpt', 'transformer', 'bert', 'tensorflow', 'pytorch',
    'scikit-learn', 'pandas', 'numpy', 'jupyter', 'kaggle'
]

# Chrome Options for Selenium
CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--disable-javascript",
    f"--user-agent={USER_AGENT}"
]

# Scraping Limits
MAX_JOBS_PER_SOURCE = 20
MAX_JOBS_PER_SEARCH = 10
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 10

# Validation
if not all([NOTION_TOKEN, AI_JOBS_DATABASE_ID, CHANGE_LOG_DATABASE_ID]):
    print("⚠️  Warning: Missing required environment variables")
    print(f"NOTION_TOKEN: {'✅' if NOTION_TOKEN else '❌'}")
    print(f"AI_JOBS_DATABASE_ID: {'✅' if AI_JOBS_DATABASE_ID else '❌'}")
    print(f"CHANGE_LOG_DATABASE_ID: {'✅' if CHANGE_LOG_DATABASE_ID else '❌'}")