#!/usr/bin/env python3
"""
Website Analyzer for Auto Scraping Type Detection
Analyzes website structure and determines the best scraping strategy
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple


class WebsiteAnalyzer:
    """Analyzes websites to determine optimal scraping strategy"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
        
    def analyze_website(self, url: str) -> Dict[str, any]:
        """
        Comprehensive website analysis to determine best scraping strategy
        
        Returns:
            Dict containing analysis results and recommended strategy
        """
        analysis = {
            'url': url,
            'timestamp': time.time(),
            'api_detected': False,
            'javascript_heavy': False,
            'simple_html': False,
            'anti_bot_detected': False,
            'spa_detected': False,
            'job_board_patterns': False,
            'response_time': 0,
            'status_code': None,
            'recommended_strategy': 'selenium',  # default fallback
            'confidence': 0.0,
            'analysis_details': {},
            'error': None
        }
        
        try:
            # Step 1: Basic connectivity test
            start_time = time.time()
            response = self._test_basic_request(url)
            analysis['response_time'] = time.time() - start_time
            
            if response is None:
                analysis['error'] = "Failed to connect to website"
                return analysis
                
            analysis['status_code'] = response.status_code
            
            # Step 2: Check for API endpoints
            analysis['api_detected'] = self._detect_api_endpoints(url, response)
            
            # Step 3: Analyze HTML content
            if response.text:
                soup = BeautifulSoup(response.text, 'html.parser')
                analysis['javascript_heavy'] = self._analyze_javascript_dependency(soup, response.text)
                analysis['spa_detected'] = self._detect_spa_patterns(soup, response.text)
                analysis['job_board_patterns'] = self._detect_job_board_patterns(soup, response.text)
                analysis['simple_html'] = self._analyze_html_simplicity(soup)
                
            # Step 4: Anti-bot detection
            analysis['anti_bot_detected'] = self._detect_anti_bot_measures(response)
            
            # Step 5: Determine strategy
            strategy, confidence = self._determine_strategy(analysis)
            analysis['recommended_strategy'] = strategy
            analysis['confidence'] = confidence
            
        except Exception as e:
            analysis['error'] = str(e)
            
        return analysis
    
    def _test_basic_request(self, url: str) -> Optional[requests.Response]:
        """Test basic HTTP request to the URL"""
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            return response
        except Exception as e:
            print(f"Basic request failed for {url}: {e}")
            return None
    
    def _detect_api_endpoints(self, base_url: str, response: requests.Response) -> bool:
        """Detect if the website has accessible API endpoints"""
        # Common API paths to test
        api_paths = [
            '/api/',
            '/api/v1/',
            '/api/v2/',
            '/api/jobs/',
            '/api/careers/',
            '/jobs.json',
            '/careers.json',
            '/graphql',
            '/api/search/',
            '/search.json'
        ]
        
        # Check if main response is JSON
        try:
            json.loads(response.text)
            return True
        except:
            pass
        
        # Check for API paths in HTML content
        if response.text:
            # Look for API endpoints mentioned in script tags or data attributes
            api_patterns = [
                r'/api/[^"\s]+',
                r'\.json[^"\s]*',
                r'graphql',
                r'endpoint["\']:\s*["\'][^"\']*api[^"\']*["\']'
            ]
            
            for pattern in api_patterns:
                if re.search(pattern, response.text, re.IGNORECASE):
                    return True
        
        # Test common API endpoints
        parsed_url = urlparse(base_url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        for path in api_paths:
            try:
                api_url = urljoin(base_domain, path)
                api_response = self.session.get(api_url, timeout=5)
                if api_response.status_code == 200:
                    # Check if response is JSON
                    try:
                        json.loads(api_response.text)
                        return True
                    except:
                        continue
            except:
                continue
                
        return False
    
    def _analyze_javascript_dependency(self, soup: BeautifulSoup, html_content: str) -> bool:
        """Analyze if the website heavily depends on JavaScript"""
        js_indicators = 0
        
        # Count script tags
        script_tags = soup.find_all('script')
        if len(script_tags) > 5:
            js_indicators += 1
            
        # Check for common SPA frameworks
        spa_patterns = [
            r'react', r'vue', r'angular', r'backbone', r'ember',
            r'app\.js', r'bundle\.js', r'main\.js', r'chunk\.js'
        ]
        
        for pattern in spa_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                js_indicators += 1
                break
        
        # Check for dynamic content indicators
        dynamic_patterns = [
            r'ng-app', r'v-app', r'data-react', r'data-vue',
            r'<div[^>]+id=["\']app["\']',
            r'<div[^>]+id=["\']root["\']',
            r'<div[^>]+class=["\'][^"\']*app[^"\']*["\']'
        ]
        
        for pattern in dynamic_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                js_indicators += 1
                break
        
        # Check for minimal content in HTML
        text_content = soup.get_text(strip=True)
        if len(text_content) < 500:  # Very little static content
            js_indicators += 1
            
        return js_indicators >= 2
    
    def _detect_spa_patterns(self, soup: BeautifulSoup, html_content: str) -> bool:
        """Detect Single Page Application patterns"""
        spa_indicators = [
            r'<div[^>]+id=["\']app["\']',
            r'<div[^>]+id=["\']root["\']',
            r'<div[^>]+class=["\'][^"\']*spa[^"\']*["\']',
            r'ng-app',
            r'data-react-root',
            r'v-app',
            r'ember-application'
        ]
        
        for pattern in spa_indicators:
            if re.search(pattern, html_content, re.IGNORECASE):
                return True
                
        # Check for minimal HTML structure (common in SPAs)
        body = soup.find('body')
        if body:
            direct_children = len([child for child in body.children if child.name])
            if direct_children <= 3:  # Very minimal HTML structure
                return True
                
        return False
    
    def _detect_job_board_patterns(self, soup: BeautifulSoup, html_content: str) -> bool:
        """Detect common job board HTML patterns"""
        job_patterns = [
            r'job[_-]?(?:card|item|listing|post)',
            r'position[_-]?(?:card|item|listing)',
            r'career[_-]?(?:card|item|listing)',
            r'vacancy[_-]?(?:card|item|listing)',
            r'role[_-]?(?:card|item|listing)',
            r'opening[_-]?(?:card|item|listing)'
        ]
        
        # Check class names and IDs
        for element in soup.find_all(['div', 'article', 'section'], class_=True):
            classes = ' '.join(element.get('class', []))
            for pattern in job_patterns:
                if re.search(pattern, classes, re.IGNORECASE):
                    return True
                    
        # Check for job-related text content
        job_keywords = ['apply now', 'job title', 'company name', 'location', 'salary', 'full-time', 'part-time']
        text_content = html_content.lower()
        
        keyword_count = sum(1 for keyword in job_keywords if keyword in text_content)
        return keyword_count >= 3
    
    def _analyze_html_simplicity(self, soup: BeautifulSoup) -> bool:
        """Determine if the HTML structure is simple enough for basic scraping"""
        # Check if essential content is readily available in HTML
        has_headings = len(soup.find_all(['h1', 'h2', 'h3', 'h4'])) > 0
        has_links = len(soup.find_all('a')) > 5
        has_text_content = len(soup.get_text(strip=True)) > 200
        
        # Check for complex dynamic structures
        complex_indicators = len(soup.find_all(['template', 'script'])) > 10
        
        return has_headings and has_links and has_text_content and not complex_indicators
    
    def _detect_anti_bot_measures(self, response: requests.Response) -> bool:
        """Detect anti-bot measures"""
        anti_bot_indicators = [
            'cloudflare',
            'captcha',
            'bot detection',
            'please verify',
            'access denied',
            'blocked',
            'rate limit'
        ]
        
        content_lower = response.text.lower()
        
        for indicator in anti_bot_indicators:
            if indicator in content_lower:
                return True
                
        # Check response headers
        headers = response.headers
        if 'cf-ray' in headers:  # Cloudflare
            return True
            
        if response.status_code in [403, 429]:  # Forbidden or rate limited
            return True
            
        return False
    
    def _determine_strategy(self, analysis: Dict) -> Tuple[str, float]:
        """Determine the best scraping strategy based on analysis"""
        confidence = 0.0
        
        # API Strategy (highest priority)
        if analysis['api_detected'] and not analysis['anti_bot_detected']:
            return 'api', 0.9
            
        # Requests Strategy (medium priority)
        if (analysis['simple_html'] and 
            not analysis['javascript_heavy'] and 
            not analysis['spa_detected'] and
            not analysis['anti_bot_detected']):
            confidence = 0.8
            if analysis['job_board_patterns']:
                confidence = 0.85
            return 'requests', confidence
            
        # Selenium Strategy (fallback)
        confidence = 0.6
        if analysis['javascript_heavy'] or analysis['spa_detected']:
            confidence = 0.8
        if analysis['anti_bot_detected']:
            confidence = 0.4  # Lower confidence due to potential blocking
            
        return 'selenium', confidence
    
    def get_strategy_explanation(self, analysis: Dict) -> str:
        """Get human-readable explanation of the strategy choice"""
        strategy = analysis['recommended_strategy']
        confidence = analysis['confidence']
        
        explanations = {
            'api': f"API endpoints detected. Direct API access recommended (confidence: {confidence:.1%})",
            'requests': f"Simple HTML structure detected. HTTP requests with parsing recommended (confidence: {confidence:.1%})",
            'selenium': f"Complex JavaScript/SPA detected or fallback needed. Browser automation recommended (confidence: {confidence:.1%})"
        }
        
        explanation = explanations.get(strategy, f"Unknown strategy: {strategy}")
        
        # Add warnings
        warnings = []
        if analysis['anti_bot_detected']:
            warnings.append("⚠️ Anti-bot measures detected - scraping may be challenging")
        if analysis['response_time'] > 5:
            warnings.append("⚠️ Slow response time detected")
        if analysis['error']:
            warnings.append(f"⚠️ Analysis error: {analysis['error']}")
            
        if warnings:
            explanation += "\n" + "\n".join(warnings)
            
        return explanation


def main():
    """Test the analyzer"""
    analyzer = WebsiteAnalyzer()
    
    test_urls = [
        'https://jobs.ashbyhq.com/openai',
        'https://www.linkedin.com/jobs/search/',
        'https://careers.google.com/jobs/results/'
    ]
    
    for url in test_urls:
        print(f"\n🔍 Analyzing: {url}")
        analysis = analyzer.analyze_website(url)
        print(f"Strategy: {analysis['recommended_strategy']}")
        print(f"Confidence: {analysis['confidence']:.1%}")
        print(analyzer.get_strategy_explanation(analysis))


if __name__ == "__main__":
    main()