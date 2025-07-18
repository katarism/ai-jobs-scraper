#!/usr/bin/env python3
"""
Test script for AI Jobs Japan Scraper
"""

import time
from datetime import datetime
from scraper import AIJobsScraper
from selenium.webdriver.common.by import By

def test_scraper():
    """Test the scraper with limited scope"""
    print("🧪 Testing AI Jobs Japan Scraper...")
    print(f"📅 Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    scraper = AIJobsScraper()
    
    # Test Notion connection
    print("\n🔗 Testing Notion connection...")
    if not scraper.notion.test_connection():
        print("❌ Cannot connect to Notion. Test failed.")
        return False
    
    print("✅ Notion connection successful!")
    
    # Test driver setup
    print("\n🚗 Testing web driver setup...")
    if not scraper.setup_driver():
        print("❌ Cannot setup web driver. Test failed.")
        return False
    
    print("✅ Web driver setup successful!")
    
    try:
        # Test a single source (LinkedIn) with limited scope
        print("\n🔍 Testing LinkedIn scraping (limited scope)...")
        
        # Test with just one search term
        test_url = "https://www.linkedin.com/jobs/search/?keywords=AI%20engineer&location=Japan"
        print(f"📄 Testing URL: {test_url}")
        
        scraper.driver.get(test_url)
        time.sleep(5)
        
        # Try to find job cards
        selectors = [
            ".job-search-card",
            ".job-card-container",
            ".job-card",
            "[data-job-id]"
        ]
        
        job_cards = []
        for selector in selectors:
            try:
                job_cards = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards:
                    print(f"✅ Found {len(job_cards)} job cards with selector: {selector}")
                    break
            except:
                continue
        
        if not job_cards:
            print("❌ No job cards found. Test failed.")
            return False
        
        # Test extracting job data from first card
        print("\n📝 Testing job data extraction...")
        try:
            job_data = scraper._extract_linkedin_job(job_cards[0])
            if job_data:
                print(f"✅ Successfully extracted job data:")
                print(f"   Title: {job_data.get('title', 'N/A')}")
                print(f"   Company: {job_data.get('company', 'N/A')}")
                print(f"   Location: {job_data.get('location', 'N/A')}")
                print(f"   Source: {job_data.get('source', 'N/A')}")
                
                # Test AI relevance check
                is_ai_related = scraper._is_ai_related(job_data)
                print(f"   AI Related: {is_ai_related}")
                
                # Test Notion job creation (if AI related)
                if is_ai_related:
                    print("\n💾 Testing Notion job creation...")
                    if not scraper.notion.check_job_exists(job_data['title'], job_data['company']):
                        if scraper.notion.create_job_entry(job_data):
                            print("✅ Successfully created job entry in Notion!")
                            scraper.total_added += 1
                        else:
                            print("❌ Failed to create job entry in Notion")
                    else:
                        print("⏭️  Job already exists in Notion")
                
            else:
                print("❌ Failed to extract job data")
                return False
                
        except Exception as e:
            print(f"❌ Error extracting job data: {e}")
            return False
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        scraper.cleanup_driver()

if __name__ == "__main__":
    success = test_scraper()
    if success:
        print("\n✅ Scraper test completed successfully!")
    else:
        print("\n❌ Scraper test failed!") 