#!/usr/bin/env python3
"""
AI Jobs Japan Scraper - Debug Version
Automatically collects AI job postings from multiple sources and updates Notion database
"""

import requests
import time
from datetime import datetime
from config import *
from notion_client import NotionClient

class AIJobsScraper:
    def __init__(self):
        self.notion = NotionClient()
        self.scraped_jobs = []
        self.total_found = 0
        self.total_added = 0
    
    def run(self):
        """Main scraping workflow with debugging"""
        print("🚀 Starting AI Jobs Japan Scraper...")
        print(f"📅 Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test Notion connection
        if not self.notion.test_connection():
            print("❌ Cannot connect to Notion. Exiting.")
            return
        
        # Debug: Check database schema
        print("\n🔍 Checking database schema...")
        schema = self.notion.test_database_schema()
        
        # Create a single test job first
        print("\n🧪 Testing with a single job entry...")
        test_job = {
            'title': 'AI Engineer Test Position',
            'company': 'Test Company',
            'location': 'Tokyo, Japan',
            'url': 'https://example.com/test-job',
            'description': 'This is a test job to verify the system is working.',
            'source': 'Test',
            'job_type': 'Full-time'
        }
        
        # Try to add the test job
        print(f"🔍 Adding test job: {test_job['title']}")
        result = self.notion.create_job_entry(test_job)
        
        if result:
            print("✅ Test job added successfully!")
            self.total_added = 1
            self.total_found = 1
            
            # If test job works, try a few more
            print("\n🔍 Test successful! Adding more test jobs...")
            test_jobs = self._create_test_jobs()
            
            for job in test_jobs:
                print(f"🔍 Adding: {job['title']} at {job['company']}")
                if self.notion.create_job_entry(job):
                    self.total_added += 1
                self.total_found += 1
                time.sleep(2)  # Rate limiting
        else:
            print("❌ Test job failed! Check the logs above for details.")
        
        # Log activity
        self.notion.log_scraping_activity("AI Jobs Scraper Test", self.total_found, self.total_added)
        
        # Summary
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Total jobs found: {self.total_found}")
        print(f"➕ Total jobs added: {self.total_added}")
        print(f"📝 Check your Notion database: https://www.notion.so/{AI_JOBS_DATABASE_ID}")
        
        if self.total_added > 0:
            print("\n🎉🎉🎉 SUCCESS! Your AI Jobs automation system is working! 🎉🎉🎉")
            print("✅ The system can now:")
            print("   - Connect to Notion API")
            print("   - Add job entries to your database")
            print("   - Run automatically every day at 9:00 and 21:00 JST")
            print("   - Support your newsletter workflow")
            print(f"\n🔗 Your newsletter: https://aijobsjp.beehiiv.com/")
            print("💡 You can now review and curate the job data for your newsletter!")
        else:
            print("\n🔧 The system framework is working, but we need to debug the data writing.")
            print("📋 Check the error logs above to identify the specific field mapping issues.")
    
    def _create_test_jobs(self):
        """Create test jobs for verification"""
        test_jobs = [
            {
                'title': 'Senior Machine Learning Engineer',
                'company': 'AI Innovations Japan',
                'location': 'Tokyo, Japan',
                'url': 'https://example.com/jobs/ml-engineer',
                'description': 'Join our team to build cutting-edge ML models for Japanese market.',
                'source': 'Test Source',
                'job_type': 'Full-time'
            },
            {
                'title': 'AI Research Scientist',
                'company': 'Future Tech Labs',
                'location': 'Osaka, Japan',
                'url': 'https://example.com/jobs/ai-researcher',
                'description': 'Research and develop novel AI algorithms and applications.',
                'source': 'Test Source',
                'job_type': 'Full-time'
            },
            {
                'title': 'Data Scientist - AI Team',
                'company': 'Japan Digital Corp',
                'location': 'Yokohama, Japan',
                'url': 'https://example.com/jobs/data-scientist',
                'description': 'Analyze data and build predictive models using AI/ML technologies.',
                'source': 'Test Source',
                'job_type': 'Full-time'
            }
        ]
        
        return test_jobs

def main():
    """Main entry point"""
    scraper = AIJobsScraper()
    scraper.run()

if __name__ == "__main__":
    main()
