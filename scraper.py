#!/usr/bin/env python3
"""
AI Jobs Japan Scraper
Automatically collects AI job postings from multiple sources and updates Notion database
"""

import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config import *
from notion_client import NotionClient

class AIJobsScraper:
    def __init__(self):
        self.notion = NotionClient()
        self.scraped_jobs = []
        self.total_found = 0
        self.total_added = 0
    
    def run(self):
        """Main scraping workflow"""
        print("🚀 Starting AI Jobs Japan Scraper...")
        print(f"📅 Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test Notion connection
        if not self.notion.test_connection():
            print("❌ Cannot connect to Notion. Exiting.")
            return
        
        # Scrape each enabled source
        for source_key, source_config in JOB_SOURCES.items():
            if source_config.get('enabled', False):
                print(f"\n🔍 Scraping {source_config['name']}...")
                
                try:
                    if source_config.get('type') == 'selenium':
                        jobs = self._scrape_with_selenium(source_key, source_config)
                    else:
                        jobs = self._scrape_with_api(source_key, source_config)
                    
                    # Process and add jobs
                    added_count = self._process_jobs(jobs, source_config['name'])
                    
                    # Log activity
                    self.notion.log_scraping_activity(
                        source_config['name'], 
                        len(jobs), 
                        added_count
                    )
                    
                    self.total_found += len(jobs)
                    self.total_added += added_count
                    
                except Exception as e:
                    print(f"❌ Error scraping {source_config['name']}: {e}")
                    self.notion.log_scraping_activity(
                        source_config['name'], 
                        0, 
                        0, 
                        f"Error: {str(e)}"
                    )
        
        # Summary
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Total jobs found: {self.total_found}")
        print(f"➕ Total jobs added: {self.total_added}")
        print(f"📝 Check your Notion database: https://www.notion.so/{AI_JOBS_DATABASE_ID}")
    
    def _scrape_with_api(self, source_key, source_config):
        """Scrape jobs using API calls"""
        jobs = []
        
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(source_config['api_url'], headers=headers, timeout=30)
            response.raise_for_status()
            
            if source_key == 'openai':
                jobs = self._parse_openai_jobs(response.json())
            elif source_key == 'xai':
                jobs = self._parse_xai_jobs(response.json())
            
        except Exception as e:
            print(f"❌ API scraping error for {source_config['name']}: {e}")
        
        return jobs
    
    def _scrape_with_selenium(self, source_key, source_config):
        """Scrape jobs using Selenium for dynamic content"""
        jobs = []
        driver = None
        
        try:
            # Setup Chrome driver
            chrome_options = Options()
            for option in CHROME_OPTIONS:
                chrome_options.add_argument(option)
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Navigate and scrape
            driver.get(source_config['url'])
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            if source_key == 'mercari':
                jobs = self._parse_mercari_jobs(driver)
            
        except Exception as e:
            print(f"❌ Selenium scraping error for {source_config['name']}: {e}")
        
        finally:
            if driver:
                driver.quit()
        
        return jobs
    
    def _parse_openai_jobs(self, data):
        """Parse OpenAI jobs data"""
        jobs = []
        
        try:
            for job in data.get('jobs', []):
                # Filter for Japan or remote positions
                location = job.get('location', '').lower()
                if 'japan' in location or 'remote' in location or 'tokyo' in location:
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': 'OpenAI',
                        'location': job.get('location', 'Japan'),
                        'url': job.get('absolute_url', ''),
                        'description': job.get('description', '')[:500],
                        'source': 'OpenAI',
                        'job_type': job.get('employment_type', 'Full-time')
                    })
        except Exception as e:
            print(f"❌ Error parsing OpenAI jobs: {e}")
        
        return jobs
    
    def _parse_xai_jobs(self, data):
        """Parse xAI jobs data"""
        jobs = []
        
        try:
            for job in data.get('positions', []):
                # Filter for relevant positions
                location = job.get('location', '').lower()
                if 'japan' in location or 'remote' in location or 'asia' in location:
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': 'xAI',
                        'location': job.get('location', 'Japan'),
                        'url': job.get('url', ''),
                        'description': job.get('description', '')[:500],
                        'source': 'xAI',
                        'job_type': 'Full-time'
                    })
        except Exception as e:
            print(f"❌ Error parsing xAI jobs: {e}")
        
        return jobs
    
    def _parse_mercari_jobs(self, driver):
        """Parse Mercari jobs using Selenium"""
        jobs = []
        
        try:
            # Wait for job listings to load
            job_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job-listing, .career-item, [data-testid*='job']"))
            )
            
            for element in job_elements[:10]:  # Limit to first 10 jobs
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, "h3, .job-title, [data-testid*='title']")
                    title = title_elem.text.strip()
                    
                    # Look for AI/ML related keywords
                    if any(keyword in title.lower() for keyword in ['ai', 'ml', 'machine learning', 'data', 'engineer']):
                        # Get job URL
                        link_elem = element.find_element(By.CSS_SELECTOR, "a")
                        job_url = link_elem.get_attribute('href')
                        
                        jobs.append({
                            'title': title,
                            'company': 'Mercari',
                            'location': 'Tokyo, Japan',
                            'url': job_url,
                            'description': f'Engineering position at Mercari - {title}',
                            'source': 'Mercari',
                            'job_type': 'Full-time'
                        })
                
                except Exception as e:
                    continue  # Skip problematic elements
        
        except Exception as e:
            print(f"❌ Error parsing Mercari jobs: {e}")
        
        return jobs
    
    def _process_jobs(self, jobs, source_name):
        """Process scraped jobs and add to Notion"""
        added_count = 0
        
        for job in jobs:
            try:
                # Check for duplicates
                if not self.notion.check_job_exists(job['title'], job['company']):
                    # Add to Notion
                    if self.notion.create_job_entry(job):
                        added_count += 1
                    
                    # Rate limiting
                    time.sleep(1)
                else:
                    print(f"⏭️  Skipping duplicate: {job['title']} at {job['company']}")
            
            except Exception as e:
                print(f"❌ Error processing job {job.get('title', 'Unknown')}: {e}")
        
        print(f"✅ {source_name}: {len(jobs)} found, {added_count} added")
        return added_count

def main():
    """Main entry point"""
    scraper = AIJobsScraper()
    scraper.run()

if __name__ == "__main__":
    main()