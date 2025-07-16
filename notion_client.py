import requests
import json
from datetime import datetime
from config import *
from rate_limiter import RateLimiter

class NotionClient:
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {NOTION_TOKEN}',
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        }
        self.rate_limiter = RateLimiter()
    
    def _make_request(self, method, url, data=None):
        """Make rate-limited request to Notion API"""
        self.rate_limiter.wait()
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Notion API error: {e}")
            return None
    
    def create_job_entry(self, job_data):
        """Create new job entry in Notion database"""
        url = f"{NOTION_API_URL}/pages"
        
        # Determine AI relevance level
        ai_level = self._calculate_ai_relevance(job_data.get('title', ''), job_data.get('description', ''))
        
        notion_data = {
            "parent": {"database_id": AI_JOBS_DATABASE_ID},
            "properties": {
                "Job Title": {
                    "title": [{"text": {"content": job_data.get('title', 'Unknown')}}]
                },
                "Company": {
                    "rich_text": [{"text": {"content": job_data.get('company', 'Unknown')}}]
                },
                "Location": {
                    "rich_text": [{"text": {"content": job_data.get('location', 'Japan')}}]
                },
                "Job URL": {
                    "url": job_data.get('url', '')
                },
                "AI Relevance Level": {
                    "select": {"name": ai_level}
                },
                "Source": {
                    "select": {"name": job_data.get('source', 'Unknown')}
                },
                "Date Added": {
                    "date": {"start": datetime.now().isoformat()}
                },
                "Newsletter Status": {
                    "select": {"name": "Pending"}
                },
                "Job Type": {
                    "select": {"name": job_data.get('job_type', 'Full-time')}
                }
            }
        }
        
        # Add description if available
        if job_data.get('description'):
            notion_data["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": job_data['description'][:2000]}}]
                    }
                }
            ]
        
        result = self._make_request('POST', url, notion_data)
        if result:
            print(f"✅ Added job: {job_data.get('title')} at {job_data.get('company')}")
            return result['id']
        return None
    
    def log_scraping_activity(self, source, jobs_found, jobs_added, status="Success"):
        """Log scraping activity to change log database"""
        url = f"{NOTION_API_URL}/pages"
        
        log_data = {
            "parent": {"database_id": CHANGE_LOG_DATABASE_ID},
            "properties": {
                "Date": {
                    "date": {"start": datetime.now().isoformat()}
                },
                "Source": {
                    "select": {"name": source}
                },
                "Jobs Found": {
                    "number": jobs_found
                },
                "Jobs Added": {
                    "number": jobs_added
                },
                "Status": {
                    "select": {"name": status}
                },
                "Notes": {
                    "rich_text": [{"text": {"content": f"Automated scraping run - Found {jobs_found}, Added {jobs_added}"}}]
                }
            }
        }
        
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
                        "rich_text": {"contains": company}
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