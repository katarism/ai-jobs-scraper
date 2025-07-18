#!/usr/bin/env python3
"""
AI Jobs Japan Scraper - Real Implementation
"""

import requests
import time
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from config import *
from notion_client import NotionClient
from website_analyzer import WebsiteAnalyzer

class AIJobsScraper:
    def __init__(self):
        self.notion = NotionClient()
        self.scraped_jobs = []
        self.total_found = 0
        self.total_added = 0
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.analyzer = WebsiteAnalyzer()
        self.analysis_cache = {}  # Cache analysis results
        
    def setup_driver(self):
        """Setup Chrome driver for Selenium"""
        chrome_options = Options()
        for option in CHROME_OPTIONS:
            chrome_options.add_argument(option)
        
        try:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            return False
    
    def cleanup_driver(self):
        """Clean up Chrome driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def get_optimal_strategy(self, source_config):
        """Determine optimal scraping strategy for a source"""
        scraping_type = source_config.get('type', 'auto')
        
        # If not auto, use specified type
        if scraping_type != 'auto':
            return scraping_type, 1.0, "Manual configuration"
        
        # Get the URL to analyze
        url = source_config.get('url') or source_config.get('base_url')
        if not url:
            return 'selenium', 0.5, "No URL provided - using selenium fallback"
        
        # Check cache first
        if url in self.analysis_cache:
            analysis = self.analysis_cache[url]
            print(f"📋 Using cached analysis for {url}")
        else:
            print(f"🔍 Analyzing website structure: {url}")
            analysis = self.analyzer.analyze_website(url)
            self.analysis_cache[url] = analysis
        
        strategy = analysis['recommended_strategy']
        confidence = analysis['confidence']
        explanation = self.analyzer.get_strategy_explanation(analysis)
        
        print(f"🎯 Selected strategy: {strategy.upper()} (confidence: {confidence:.1%})")
        print(f"📝 Reason: {explanation}")
        
        return strategy, confidence, explanation
    
    def _scrape_all_sources(self):
        """Scrape all enabled sources using optimal strategies"""
        for source_key, source_config in JOB_SOURCES.items():
            if not source_config.get('enabled', False):
                print(f"⏭️  Skipping disabled source: {source_config.get('name', source_key)}")
                continue
                
            print(f"\n🔍 Processing source: {source_config.get('name', source_key)}")
            
            try:
                # Get optimal strategy
                strategy, confidence, explanation = self.get_optimal_strategy(source_config)
                
                # Skip if confidence is too low
                if confidence < 0.3:
                    print(f"⚠️  Skipping source due to low confidence ({confidence:.1%})")
                    continue
                
                # Execute based on strategy
                if strategy == 'api':
                    self._scrape_with_api(source_key, source_config)
                elif strategy == 'requests':
                    self._scrape_with_requests(source_key, source_config)
                else:  # selenium fallback
                    self._scrape_with_selenium(source_key, source_config)
                    
            except Exception as e:
                print(f"❌ Error scraping {source_key}: {e}")
                continue
                
            time.sleep(REQUEST_DELAY)  # Rate limiting between sources
    
    def _scrape_with_api(self, source_key, source_config):
        """Scrape using API endpoint"""
        print(f"🔌 Using API strategy for {source_config.get('name', source_key)}")
        
        url = source_config.get('url')
        if not url:
            print("❌ No API URL configured")
            return
            
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Handle different API response formats
                    jobs = self._extract_jobs_from_api_response(data, source_config)
                    
                    for job in jobs[:MAX_JOBS_PER_SOURCE]:
                        if self._is_ai_related(job):
                            self._process_job(job)
                            
                except json.JSONDecodeError:
                    print("❌ Failed to parse API response as JSON")
            else:
                print(f"❌ API returned status code: {response.status_code}")
                # Fallback to selenium
                self._scrape_with_selenium(source_key, source_config)
                
        except Exception as e:
            print(f"❌ API scraping failed: {e}")
            # Fallback to selenium
            self._scrape_with_selenium(source_key, source_config)
    
    def _scrape_with_requests(self, source_key, source_config):
        """Scrape using simple HTTP requests and BeautifulSoup"""
        print(f"🌐 Using requests strategy for {source_config.get('name', source_key)}")
        
        url = source_config.get('url') or source_config.get('base_url')
        if not url:
            print("❌ No URL configured")
            return
            
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                jobs = self._extract_jobs_from_html(soup, source_config, source_key)
                
                for job in jobs[:MAX_JOBS_PER_SOURCE]:
                    if self._is_ai_related(job):
                        self._process_job(job)
            else:
                print(f"❌ HTTP request returned status code: {response.status_code}")
                # Fallback to selenium
                self._scrape_with_selenium(source_key, source_config)
                
        except Exception as e:
            print(f"❌ Requests scraping failed: {e}")
            # Fallback to selenium
            self._scrape_with_selenium(source_key, source_config)
    
    def _scrape_with_selenium(self, source_key, source_config):
        """Scrape using Selenium (browser automation)"""
        print(f"🤖 Using selenium strategy for {source_config.get('name', source_key)}")
        
        # Use existing selenium-based methods based on source
        if source_key == 'linkedin':
            self._scrape_linkedin_jobs()
        elif source_key == 'indeed':
            self._scrape_indeed_jobs()
        elif source_key == 'mercari':
            self._scrape_mercari_jobs()
        elif source_key == 'rakuten':
            self._scrape_rakuten_jobs()
        elif source_key == 'line':
            self._scrape_line_jobs()
        elif source_key == 'google':
            self._scrape_google_jobs()
        elif source_key == 'amazon':
            self._scrape_amazon_jobs()
        else:
            # Generic selenium scraping for new sources
            self._scrape_generic_selenium(source_key, source_config)
    
    def _extract_jobs_from_api_response(self, data, source_config):
        """Extract jobs from API response data"""
        jobs = []
        
        # Common API response formats
        if isinstance(data, list):
            jobs_data = data
        elif isinstance(data, dict):
            # Try common keys for job lists
            jobs_data = (data.get('jobs') or 
                        data.get('results') or 
                        data.get('hits') or 
                        data.get('data') or 
                        data.get('items') or [])
        else:
            jobs_data = []
        
        for job_data in jobs_data:
            if isinstance(job_data, dict):
                job = {
                    'title': job_data.get('title') or job_data.get('name') or '',
                    'company': job_data.get('company') or source_config.get('name', 'Unknown'),
                    'location': job_data.get('location') or job_data.get('city') or 'Japan',
                    'url': job_data.get('url') or job_data.get('link') or '',
                    'description': job_data.get('description') or job_data.get('summary') or '',
                    'source': source_config.get('name', 'API'),
                    'job_type': job_data.get('type') or 'Full-time'
                }
                if job['title']:  # Only add if has title
                    jobs.append(job)
        
        return jobs
    
    def _extract_jobs_from_html(self, soup, source_config, source_key):
        """Extract jobs from HTML using BeautifulSoup"""
        jobs = []
        
        # Common job listing selectors
        job_selectors = [
            '.job-card', '.job-listing', '.job-item', '.job-post',
            '.position-card', '.career-item', '.opening-item',
            '[data-job]', '[data-position]', '.posting'
        ]
        
        job_elements = []
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                job_elements = elements
                break
        
        for element in job_elements:
            job = self._extract_job_from_element(element, source_config)
            if job:
                jobs.append(job)
        
        return jobs
    
    def _extract_job_from_element(self, element, source_config):
        """Extract job data from a single HTML element"""
        try:
            # Extract title
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.job-title', '.position-title']
            title = ""
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # Extract company (default to source name)
            company_selectors = ['.company', '.company-name', '.employer']
            company = source_config.get('name', 'Unknown')
            for selector in company_selectors:
                company_elem = element.select_one(selector)
                if company_elem:
                    company = company_elem.get_text(strip=True)
                    break
            
            # Extract location
            location_selectors = ['.location', '.job-location', '.city']
            location = "Japan"
            for selector in location_selectors:
                location_elem = element.select_one(selector)
                if location_elem:
                    location = location_elem.get_text(strip=True)
                    break
            
            # Extract URL
            url = ""
            link_elem = element.select_one('a')
            if link_elem and link_elem.get('href'):
                url = link_elem.get('href')
                # Make absolute URL if relative
                if url.startswith('/'):
                    base_url = source_config.get('url', '')
                    if base_url:
                        from urllib.parse import urljoin
                        url = urljoin(base_url, url)
            
            if not title:
                return None
                
            return {
                'title': title,
                'company': company,
                'location': location,
                'url': url,
                'description': f"Position at {company}. {title}",
                'source': source_config.get('name', 'Web'),
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            print(f"❌ Error extracting job from element: {e}")
            return None
    
    def _scrape_generic_selenium(self, source_key, source_config):
        """Generic selenium scraping for new sources"""
        try:
            url = source_config.get('url')
            if not url:
                print("❌ No URL configured for generic selenium scraping")
                return
                
            self.driver.get(url)
            time.sleep(5)
            
            # Use similar approach as existing selenium methods
            selectors = [
                ".job-card", ".job-listing", ".job-item", ".job-post",
                ".position-card", ".career-item", "[data-job]"
            ]
            
            job_cards = []
            for selector in selectors:
                try:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        break
                except:
                    continue
            
            for card in job_cards[:MAX_JOBS_PER_SOURCE]:
                try:
                    job_data = self._extract_selenium_job_generic(card, source_config)
                    if job_data and self._is_ai_related(job_data):
                        self._process_job(job_data)
                except Exception as e:
                    print(f"❌ Error extracting job: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Generic selenium scraping failed: {e}")
    
    def _extract_selenium_job_generic(self, card, source_config):
        """Generic job extraction from selenium element"""
        try:
            # Try multiple selectors for title
            title_selectors = [
                "h1", "h2", "h3", "h4", ".title", ".job-title", 
                ".position-title", ".posting-title"
            ]
            
            title = ""
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # Extract location
            location_selectors = [".location", ".job-location", ".city", ".address"]
            location = "Japan"
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    location = location_elem.text.strip()
                    if location:
                        break
                except:
                    continue
            
            # Get URL
            job_url = ""
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a")
                job_url = link_elem.get_attribute("href")
            except:
                pass
            
            if not title:
                return None
            
            return {
                'title': title,
                'company': source_config.get('name', 'Unknown'),
                'location': location,
                'url': job_url,
                'description': f"Position at {source_config.get('name', 'Company')}. {title}",
                'source': source_config.get('name', 'Web'),
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            print(f"❌ Error in generic selenium extraction: {e}")
            return None
    
    def run(self):
        """Main scraping workflow"""
        print("🚀 Starting AI Jobs Japan Scraper...")
        print(f"📅 Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test Notion connection
        if not self.notion.test_connection():
            print("❌ Cannot connect to Notion. Exiting.")
            return
        
        # Setup Selenium driver
        if not self.setup_driver():
            print("❌ Cannot setup web driver. Exiting.")
            return
        
        try:
            # Scrape from configured sources using optimal strategy
            self._scrape_all_sources()
            
        finally:
            self.cleanup_driver()
        
        # Log activity
        self.notion.log_scraping_activity("AI Jobs Scraper", self.total_found, self.total_added)
        
        # Summary
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Total jobs found: {self.total_found}")
        print(f"➕ Total jobs added: {self.total_added}")
        print(f"📝 Check your Notion database: https://www.notion.so/{AI_JOBS_DATABASE_ID}")
    
    def _scrape_linkedin_jobs(self):
        """Scrape AI jobs from LinkedIn"""
        print("\n🔍 Scraping LinkedIn AI jobs...")
        
        source_config = JOB_SOURCES['linkedin']
        
        for term in source_config['search_terms']:
            try:
                url = f"{source_config['base_url']}?keywords={term.replace(' ', '%20')}&location=Japan"
                print(f"📄 Searching: {term}")
                
                self.driver.get(url)
                time.sleep(5)  # Wait for page load
                
                # Scroll to load more jobs
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                # Try multiple selectors for job cards
                selectors = [
                    ".job-search-card",
                    ".job-card-container",
                    ".job-card",
                    "[data-job-id]"
                ]
                
                job_cards = []
                for selector in selectors:
                    try:
                        job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if job_cards:
                            break
                    except:
                        continue
                
                for card in job_cards[:MAX_JOBS_PER_SEARCH]:
                    try:
                        job_data = self._extract_linkedin_job(card)
                        if job_data and self._is_ai_related(job_data):
                            self._process_job(job_data)
                    except Exception as e:
                        print(f"❌ Error extracting LinkedIn job: {e}")
                        continue
                
                time.sleep(REQUEST_DELAY)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error scraping LinkedIn for {term}: {e}")
                continue
    
    def _extract_linkedin_job(self, card):
        """Extract job data from LinkedIn job card"""
        try:
            # Try multiple selectors for each field
            title_selectors = [
                ".job-search-card__title",
                ".job-card-list__title",
                "h3",
                "[data-test-job-card-list__title]"
            ]
            
            company_selectors = [
                ".job-search-card__subtitle",
                ".job-card-container__company-name",
                ".job-card-container__subtitle"
            ]
            
            location_selectors = [
                ".job-search-card__location",
                ".job-card-container__metadata-item"
            ]
            
            # Extract title
            title = ""
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # Extract company
            company = ""
            for selector in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, selector)
                    company = company_elem.text.strip()
                    if company:
                        break
                except:
                    continue
            
            # Extract location
            location = ""
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    location = location_elem.text.strip()
                    if location:
                        break
                except:
                    continue
            
            # Get job URL
            job_url = ""
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a")
                job_url = link_elem.get_attribute("href")
            except:
                pass
            
            if not title or not company:
                return None
            
            # Get description (basic)
            description = f"AI/ML position at {company}. Apply through LinkedIn."
            
            return {
                'title': title,
                'company': company,
                'location': location or "Japan",
                'url': job_url,
                'description': description,
                'source': 'LinkedIn',
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            print(f"❌ Error extracting LinkedIn job data: {e}")
            return None
    
    def _scrape_indeed_jobs(self):
        """Scrape AI jobs from Indeed"""
        print("\n🔍 Scraping Indeed AI jobs...")
        
        source_config = JOB_SOURCES['indeed']
        
        for term in source_config['search_terms']:
            try:
                url = f"{source_config['base_url']}?q={term.replace(' ', '+')}&l=Japan"
                print(f"📄 Searching: {term}")
                
                self.driver.get(url)
                time.sleep(5)
                
                # Try multiple selectors for job cards
                selectors = [
                    ".job_seen_beacon",
                    ".jobsearch-ResultsList .job_seen_beacon",
                    ".job_seen_beacon .job_seen_beacon",
                    "[data-jk]"
                ]
                
                job_cards = []
                for selector in selectors:
                    try:
                        job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if job_cards:
                            break
                    except:
                        continue
                
                for card in job_cards[:MAX_JOBS_PER_SEARCH]:
                    try:
                        job_data = self._extract_indeed_job(card)
                        if job_data and self._is_ai_related(job_data):
                            self._process_job(job_data)
                    except Exception as e:
                        print(f"❌ Error extracting Indeed job: {e}")
                        continue
                
                time.sleep(REQUEST_DELAY)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error scraping Indeed for {term}: {e}")
                continue
    
    def _extract_indeed_job(self, card):
        """Extract job data from Indeed job card"""
        try:
            # Try multiple selectors for each field
            title_selectors = [
                "h2.jobTitle span[title]",
                ".jobTitle a",
                "h2 a",
                "[data-testid='jobsearch-JobComponent-title']"
            ]
            
            company_selectors = [
                ".companyName",
                ".company",
                "[data-testid='jobsearch-JobComponent-company']"
            ]
            
            location_selectors = [
                ".companyLocation",
                ".location",
                "[data-testid='jobsearch-JobComponent-location']"
            ]
            
            # Extract title
            title = ""
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.get_attribute("title") or title_elem.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # Extract company
            company = ""
            for selector in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, selector)
                    company = company_elem.text.strip()
                    if company:
                        break
                except:
                    continue
            
            # Extract location
            location = ""
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    location = location_elem.text.strip()
                    if location:
                        break
                except:
                    continue
            
            # Get job URL
            job_url = ""
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
                job_url = "https://jp.indeed.com" + link_elem.get_attribute("href")
            except:
                pass
            
            if not title or not company:
                return None
            
            # Get description (basic)
            description = f"AI/ML position at {company}. Apply through Indeed."
            
            return {
                'title': title,
                'company': company,
                'location': location or "Japan",
                'url': job_url,
                'description': description,
                'source': 'Indeed',
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            print(f"❌ Error extracting Indeed job data: {e}")
            return None
    
    def _scrape_mercari_jobs(self):
        """Scrape jobs from Mercari careers"""
        print("\n🔍 Scraping Mercari AI jobs...")
        
        try:
            url = JOB_SOURCES['mercari']['url']
            self.driver.get(url)
            time.sleep(5)
            
            # Try multiple selectors for job cards
            selectors = [
                ".job-card",
                ".job-listing",
                ".position-card",
                "[data-testid='job-card']"
            ]
            
            job_cards = []
            for selector in selectors:
                try:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        break
                except:
                    continue
            
            for card in job_cards[:MAX_JOBS_PER_SOURCE]:
                try:
                    job_data = self._extract_mercari_job(card)
                    if job_data and self._is_ai_related(job_data):
                        self._process_job(job_data)
                except Exception as e:
                    print(f"❌ Error extracting Mercari job: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error scraping Mercari: {e}")
    
    def _extract_mercari_job(self, card):
        """Extract job data from Mercari job card"""
        try:
            # Try multiple selectors for each field
            title_selectors = [
                ".job-title",
                ".position-title",
                "h3",
                "h4"
            ]
            
            location_selectors = [
                ".job-location",
                ".location",
                ".job-meta"
            ]
            
            # Extract title
            title = ""
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # Extract location
            location = ""
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    location = location_elem.text.strip()
                    if location:
                        break
                except:
                    continue
            
            # Get job URL
            job_url = ""
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a")
                job_url = link_elem.get_attribute("href")
            except:
                pass
            
            if not title:
                return None
            
            # Mercari is the company
            company = "Mercari"
            
            description = f"Engineering position at Mercari. {title}"
            
            return {
                'title': title,
                'company': company,
                'location': location or "Japan",
                'url': job_url,
                'description': description,
                'source': 'Mercari Careers',
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            print(f"❌ Error extracting Mercari job data: {e}")
            return None
    
    def _scrape_rakuten_jobs(self):
        """Scrape jobs from Rakuten careers"""
        print("\n🔍 Scraping Rakuten AI jobs...")
        
        try:
            url = JOB_SOURCES['rakuten']['url']
            self.driver.get(url)
            time.sleep(5)
            
            # Try to search for AI/ML related jobs
            try:
                search_selectors = [
                    "input[placeholder*='search']",
                    "input[placeholder*='Search']",
                    "input[type='search']",
                    ".search-input"
                ]
                
                search_box = None
                for selector in search_selectors:
                    try:
                        search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if search_box:
                    search_box.clear()
                    search_box.send_keys("AI Machine Learning")
                    search_box.submit()
                    time.sleep(3)
            except:
                pass  # Continue without search if it fails
            
            # Try multiple selectors for job cards
            selectors = [
                ".job-listing",
                ".job-card",
                ".position-card",
                ".job-item"
            ]
            
            job_cards = []
            for selector in selectors:
                try:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        break
                except:
                    continue
            
            for card in job_cards[:MAX_JOBS_PER_SOURCE]:
                try:
                    job_data = self._extract_rakuten_job(card)
                    if job_data and self._is_ai_related(job_data):
                        self._process_job(job_data)
                except Exception as e:
                    print(f"❌ Error extracting Rakuten job: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error scraping Rakuten: {e}")
    
    def _extract_rakuten_job(self, card):
        """Extract job data from Rakuten job card"""
        try:
            # Try multiple selectors for each field
            title_selectors = [
                ".job-title",
                ".position-title",
                "h3",
                "h4"
            ]
            
            location_selectors = [
                ".job-location",
                ".location",
                ".job-meta"
            ]
            
            # Extract title
            title = ""
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # Extract location
            location = ""
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    location = location_elem.text.strip()
                    if location:
                        break
                except:
                    continue
            
            # Get job URL
            job_url = ""
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a")
                job_url = link_elem.get_attribute("href")
            except:
                pass
            
            if not title:
                return None
            
            company = "Rakuten"
            
            description = f"AI/ML position at Rakuten. {title}"
            
            return {
                'title': title,
                'company': company,
                'location': location or "Japan",
                'url': job_url,
                'description': description,
                'source': 'Rakuten Careers',
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            print(f"❌ Error extracting Rakuten job data: {e}")
            return None
    
    def _scrape_line_jobs(self):
        """Scrape jobs from LINE careers"""
        print("\n🔍 Scraping LINE AI jobs...")
        
        try:
            url = JOB_SOURCES['line']['url']
            self.driver.get(url)
            time.sleep(5)
            
            # Try multiple selectors for job cards
            selectors = [
                ".job-position",
                ".position-card",
                ".job-listing",
                ".career-item"
            ]
            
            job_cards = []
            for selector in selectors:
                try:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        break
                except:
                    continue
            
            for card in job_cards[:MAX_JOBS_PER_SOURCE]:
                try:
                    job_data = self._extract_line_job(card)
                    if job_data and self._is_ai_related(job_data):
                        self._process_job(job_data)
                except Exception as e:
                    print(f"❌ Error extracting LINE job: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error scraping LINE: {e}")
    
    def _extract_line_job(self, card):
        """Extract job data from LINE job card"""
        try:
            # Try multiple selectors for each field
            title_selectors = [
                ".position-title",
                ".job-title",
                "h3",
                "h4"
            ]
            
            location_selectors = [
                ".position-location",
                ".location",
                ".job-meta"
            ]
            
            # Extract title
            title = ""
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # Extract location
            location = ""
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    location = location_elem.text.strip()
                    if location:
                        break
                except:
                    continue
            
            # Get job URL
            job_url = ""
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a")
                job_url = link_elem.get_attribute("href")
            except:
                pass
            
            if not title:
                return None
            
            company = "LINE"
            
            description = f"AI/ML position at LINE. {title}"
            
            return {
                'title': title,
                'company': company,
                'location': location or "Japan",
                'url': job_url,
                'description': description,
                'source': 'LINE Careers',
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            print(f"❌ Error extracting LINE job data: {e}")
            return None
    
    def _scrape_google_jobs(self):
        """Scrape jobs from Google careers"""
        print("\n🔍 Scraping Google AI jobs...")
        
        try:
            url = JOB_SOURCES['google']['url']
            self.driver.get(url)
            time.sleep(5)
            
            # Try multiple selectors for job cards
            selectors = [
                ".job-listing",
                ".job-card",
                ".position-card",
                "[data-testid='job-card']"
            ]
            
            job_cards = []
            for selector in selectors:
                try:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        break
                except:
                    continue
            
            for card in job_cards[:MAX_JOBS_PER_SOURCE]:
                try:
                    job_data = self._extract_google_job(card)
                    if job_data and self._is_ai_related(job_data):
                        self._process_job(job_data)
                except Exception as e:
                    print(f"❌ Error extracting Google job: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error scraping Google: {e}")
    
    def _extract_google_job(self, card):
        """Extract job data from Google job card"""
        try:
            # Try multiple selectors for each field
            title_selectors = [
                ".job-title",
                ".position-title",
                "h3",
                "h4"
            ]
            
            location_selectors = [
                ".job-location",
                ".location",
                ".job-meta"
            ]
            
            # Extract title
            title = ""
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # Extract location
            location = ""
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    location = location_elem.text.strip()
                    if location:
                        break
                except:
                    continue
            
            # Get job URL
            job_url = ""
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a")
                job_url = link_elem.get_attribute("href")
            except:
                pass
            
            if not title:
                return None
            
            company = "Google"
            
            description = f"AI/ML position at Google. {title}"
            
            return {
                'title': title,
                'company': company,
                'location': location or "Japan",
                'url': job_url,
                'description': description,
                'source': 'Google Careers',
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            print(f"❌ Error extracting Google job data: {e}")
            return None
    
    def _scrape_amazon_jobs(self):
        """Scrape jobs from Amazon careers API"""
        print("\n🔍 Scraping Amazon AI jobs...")
        
        try:
            url = JOB_SOURCES['amazon']['url']
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    jobs = data.get('hits', [])
                    
                    for job in jobs[:MAX_JOBS_PER_SOURCE]:
                        try:
                            job_data = self._extract_amazon_job(job)
                            if job_data and self._is_ai_related(job_data):
                                self._process_job(job_data)
                        except Exception as e:
                            print(f"❌ Error extracting Amazon job: {e}")
                            continue
                            
                except json.JSONDecodeError:
                    print("❌ Failed to parse Amazon API response")
            else:
                print(f"❌ Amazon API returned status code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error scraping Amazon: {e}")
    
    def _extract_amazon_job(self, job):
        """Extract job data from Amazon API response"""
        try:
            title = job.get('title', '')
            company = "Amazon"
            location = job.get('location', 'Japan')
            job_url = job.get('url', '')
            description = job.get('description', f"AI/ML position at Amazon. {title}")
            
            if not title:
                return None
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'url': job_url,
                'description': description,
                'source': 'Amazon Careers',
                'job_type': 'Full-time'
            }
            
        except Exception as e:
            print(f"❌ Error extracting Amazon job data: {e}")
            return None
    
    def _is_ai_related(self, job_data):
        """Check if job is AI/ML related"""
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        
        for keyword in AI_KEYWORDS:
            if keyword in title or keyword in description:
                return True
        
        return False
    
    def _process_job(self, job_data):
        """Process and add job to Notion"""
        try:
            print(f"\n📝 Processing: {job_data['title']} at {job_data['company']}")
            
            # Check for duplicates
            if not self.notion.check_job_exists(job_data['title'], job_data['company']):
                # Add to Notion
                if self.notion.create_job_entry(job_data):
                    self.total_added += 1
                    print(f"✅ Successfully added job!")
                else:
                    print(f"❌ Failed to add job")
            else:
                print(f"⏭️  Skipping duplicate job")
            
            self.total_found += 1
            
        except Exception as e:
            print(f"❌ Error processing job {job_data.get('title', 'Unknown')}: {e}")

def main():
    """Main entry point"""
    scraper = AIJobsScraper()
    scraper.run()

if __name__ == "__main__":
    main()
