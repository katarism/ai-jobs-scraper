import requests
import json
import time
from datetime import datetime
from config import *

class NotionClient:
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {NOTION_TOKEN}',
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        }
        self.last_request_time = 0
    
    def _rate_limit_wait(self):
        """Simple rate limiting - wait between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < REQUEST_DELAY:
            sleep_time = REQUEST_DELAY - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, method, url, data=None):
        """Make rate-limited request to Notion API"""
        self._rate_limit_wait()
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code >= 400:
                print(f"❌ Notion API error {response.status_code}: {response.text}")
                return None
                
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Notion API error: {e}")
            return None
    
    def create_job_entry(self, job_data):
        """Create new job entry in Notion database with simplified structure"""
        url = f"{NOTION_API_URL}/pages"
        
        # Simplified data structure - only essential fields
        notion_data = {
            "parent": {"database_id": AI_JOBS_DATABASE_ID},
            "properties": {
                "Name": {  # Most Notion databases have "Name" as title
                    "title": [{"text": {"content": job_data.get('title', 'Unknown Job')[:100]}}]
                }
            }
        }
        
        # Try to add additional fields if they exist in the database
        try:
            # Add company if possible
            if job_data.get('company'):
                notion_data["properties"]["Company"] = {
                    "rich_text": [{"text": {"content": job_data['company'][:100]}}]
                }
            
            # Add location if possible  
            if job_data.get('location'):
                notion_data["properties"]["Location"] = {
                    "rich_text": [{"text": {"content": job_data['location'][:100]}}]
                }
            
            # Add URL if possible
            if job_data.get('url'):
                notion_data["properties"]["URL"] = {
                    "url": job_data['url'][:2000]
                }
            
            # Add source if possible
            if job_data.get('source'):
                notion_data["properties"]["Source"] = {
                    "rich_text": [{"text": {"content": job_data['source'][:100]}}]
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Could not add additional fields: {e}")
        
        print(f"🔍 Attempting to create job entry: {json.dumps(notion_data, indent=2)}")
        
        result = self._make_request('POST', url, notion_data)
        if result:
            print(f"✅ Added job: {job_data.get('title')} at {job_data.get('company')}")
            return result.get('id')
        else:
            print(f"❌ Failed to add job: {job_data.get('title')}")
            return None
    
    def log_scraping_activity(self, source, jobs_found, jobs_added, status="Success"):
        """Log scraping activity to change log database with simplified structure"""
        url = f"{NOTION_API_URL}/pages"
        
        log_data = {
            "parent": {"database_id": CHANGE_LOG_DATABASE_ID},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": f"{source} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"}}]
                }
            }
        }
        
        # Try to add additional fields
        try:
            log_data["properties"]["Source"] = {
                "rich_text": [{"text": {"content": source}}]
            }
            log_data["properties"]["Jobs Found"] = {
                "number": jobs_found
            }
            log_data["properties"]["Jobs Added"] = {
                "number": jobs_added
            }
            log_data["properties"]["Status"] = {
                "rich_text": [{"text": {"content": status}}]
            }
        except Exception as e:
            print(f"⚠️  Warning: Could not add log fields: {e}")
        
        result = self._make_request('POST', url, log_data)
        if result:
            print(f"📊 Logged activity: {source} - {jobs_found} found, {jobs_added} added")
        return result
    
    def check_job_exists(self, job_title, company):
        """Simplified duplicate check - just return False to allow all entries for now"""
        print(f"🔍 Checking for duplicate: {job_title} at {company}")
        return False  # Temporarily disable duplicate checking to test basic writing
    
    def test_connection(self):
        """Test Notion API connection"""
        url = f"{NOTION_API_URL}/users/me"
        result = self._make_request('GET', url)
        
        if result:
            print(f"✅ Notion connection successful! User: {result.get('name', 'Unknown')}")
            return True
        else:
            print("❌ Notion connection failed!")
            return False
    
    def test_database_schema(self):
        """Test and print database schema to debug field names"""
        url = f"{NOTION_API_URL}/databases/{AI_JOBS_DATABASE_ID}"
        
        result = self._make_request('GET', url)
        if result:
            print("📋 Database schema:")
            properties = result.get('properties', {})
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get('type', 'unknown')
                print(f"  - {prop_name}: {prop_type}")
            return properties
        else:
            print("❌ Could not retrieve database schema")
            return None
