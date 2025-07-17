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
        """Create new job entry in Notion database with correct field types"""
        url = f"{NOTION_API_URL}/pages"
        
        # Build properties with correct field types based on database schema
        properties = {}
        
        # Job Title (title field)
        properties["Job Title"] = {
            "title": [{"text": {"content": job_data.get('title', 'Unknown Job')[:100]}}]
        }
        
        # Company (select field) - need to provide select option
        if job_data.get('company'):
            properties["Company"] = {
                "select": {"name": job_data['company'][:100]}
            }
        
        # Location (rich_text field)
        if job_data.get('location'):
            properties["Location"] = {
                "rich_text": [{"text": {"content": job_data['location'][:100]}}]
            }
        
        # Job Link (url field)
        if job_data.get('url'):
            properties["Job Link"] = {
                "url": job_data['url'][:2000]
            }
        
        # Description (rich_text field)
        if job_data.get('description'):
            properties["Description"] = {
                "rich_text": [{"text": {"content": job_data['description'][:2000]}}]
            }
        
        # Data Source (select field)
        if job_data.get('source'):
            properties["Data Source"] = {
                "select": {"name": job_data['source'][:100]}
            }
        
        # AI Relevance Level (select field)
        ai_level = self._calculate_ai_relevance(job_data.get('title', ''), job_data.get('description', ''))
        properties["AI Relevance Level"] = {
            "select": {"name": ai_level}
        }
        
        # Newsletter Status (select field)
        properties["Newsletter Status"] = {
            "select": {"name": "Pending"}
        }
        
        # Position Type (select field)
        properties["Position Type"] = {
            "select": {"name": job_data.get('job_type', 'Full-time')}
        }
        
        # Date Added (date field)
        properties["Date Added"] = {
            "date": {"start": datetime.now().isoformat()}
        }
        
        # Date Last Checked (date field)
        properties["Date Last Checked"] = {
            "date": {"start": datetime.now().isoformat()}
        }
        
        # Status (select field)
        properties["Status"] = {
            "select": {"name": "Active"}
        }
        
        notion_data = {
            "parent": {"database_id": AI_JOBS_DATABASE_ID},
            "properties": properties
        }
        
        print(f"🔍 Creating job entry: {job_data.get('title')} at {job_data.get('company')}")
        
        result = self._make_request('POST', url, notion_data)
        if result:
            print(f"✅ Added job: {job_data.get('title')} at {job_data.get('company')}")
            return result.get('id')
        else:
            print(f"❌ Failed to add job: {job_data.get('title')}")
            return None
    
    def log_scraping_activity(self, source, jobs_found, jobs_added, status="Success"):
        """Log scraping activity to change log database"""
        url = f"{NOTION_API_URL}/pages"
        
        # For change log, we need to check the schema of the change log database
        # For now, use a simple structure
        log_data = {
            "parent": {"database_id": CHANGE_LOG_DATABASE_ID},
            "properties": {
                # Assuming change log has a title field
                "Name": {
                    "title": [{"text": {"content": f"{source} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"}}]
                }
            }
        }
        
        # Try to add additional fields if they exist
        try:
            # Add as rich_text fields for maximum compatibility
            if hasattr(self, '_change_log_schema'):
                # Use cached schema if available
                pass
            else:
                # Add basic fields as rich_text
                log_data["properties"]["Source"] = {
                    "rich_text": [{"text": {"content": source}}]
                }
                log_data["properties"]["Jobs Found"] = {
                    "rich_text": [{"text": {"content": str(jobs_found)}}]
                }
                log_data["properties"]["Jobs Added"] = {
                    "rich_text": [{"text": {"content": str(jobs_added)}}]
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
        """Check if job already exists in database"""
        url = f"{NOTION_API_URL}/databases/{AI_JOBS_DATABASE_ID}/query"
        
        query_data = {
            "filter": {
                "and": [
                    {
                        "property": "Job Title",
                        "title": {"contains": job_title}
                    },
                    {
                        "property": "Company",
                        "select": {"equals": company}
                    }
                ]
            }
        }
        
        result = self._make_request('POST', url, query_data)
        if result and result.get('results'):
            return len(result['results']) > 0
        return False
    
    def _calculate_ai_relevance(self, title, description):
        """Calculate AI relevance level based on job title and description"""
        text = f"{title} {description}".lower()
        
        high_keywords = ['ai engineer', 'machine learning', 'deep learning', 'artificial intelligence', 
                        'neural network', 'computer vision', 'nlp', 'data scientist', 'ml engineer']
        
        medium_keywords = ['ai', 'automation', 'algorithm', 'analytics', 'data engineer', 
                          'software engineer', 'python', 'tensorflow', 'pytorch']
        
        low_keywords = ['tech', 'engineer', 'developer', 'software', 'programming']
        
        # Check for high relevance
        for keyword in high_keywords:
            if keyword in text:
                return "High"
        
        # Check for medium relevance  
        for keyword in medium_keywords:
            if keyword in text:
                return "Medium"
        
        # Check for low relevance
        for keyword in low_keywords:
            if keyword in text:
                return "Low"
        
        return "Unknown"
    
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
