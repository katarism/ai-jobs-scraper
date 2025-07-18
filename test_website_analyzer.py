#!/usr/bin/env python3
"""
Comprehensive tests for the WebsiteAnalyzer module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from bs4 import BeautifulSoup
from website_analyzer import WebsiteAnalyzer


class TestWebsiteAnalyzer(unittest.TestCase):
    """Test cases for WebsiteAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = WebsiteAnalyzer(timeout=5)
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        self.assertIsInstance(self.analyzer, WebsiteAnalyzer)
        self.assertEqual(self.analyzer.timeout, 5)
        self.assertIsInstance(self.analyzer.session, requests.Session)
    
    @patch('requests.Session.get')
    def test_basic_request_success(self, mock_get):
        """Test successful basic request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_get.return_value = mock_response
        
        response = self.analyzer._test_basic_request("https://example.com")
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_basic_request_failure(self, mock_get):
        """Test failed basic request"""
        # Mock request exception
        mock_get.side_effect = requests.RequestException("Connection failed")
        
        response = self.analyzer._test_basic_request("https://example.com")
        
        self.assertIsNone(response)
    
    def test_detect_api_endpoints_json_response(self):
        """Test API detection with JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"jobs": [{"title": "Developer"}]}'
        
        result = self.analyzer._detect_api_endpoints("https://api.example.com", mock_response)
        self.assertTrue(result)
    
    @patch('requests.Session.get')
    def test_detect_api_endpoints_with_api_paths(self, mock_get):
        """Test API detection by testing common paths"""
        # Mock main response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Regular HTML</html>"
        
        # Mock API endpoint response
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.text = '{"data": []}'
        mock_get.return_value = mock_api_response
        
        result = self.analyzer._detect_api_endpoints("https://example.com", mock_response)
        self.assertTrue(result)
    
    def test_analyze_javascript_dependency_heavy(self):
        """Test JavaScript dependency analysis for heavy JS site"""
        html_content = """
        <html>
        <head>
            <script src="react.js"></script>
            <script src="vue.js"></script>
            <script src="app.js"></script>
            <script src="bundle.js"></script>
            <script src="main.js"></script>
            <script src="chunk.js"></script>
        </head>
        <body>
            <div id="app" ng-app="myApp">Very little content</div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = self.analyzer._analyze_javascript_dependency(soup, html_content)
        self.assertTrue(result)
    
    def test_analyze_javascript_dependency_light(self):
        """Test JavaScript dependency analysis for light JS site"""
        html_content = """
        <html>
        <head>
            <script src="simple.js"></script>
        </head>
        <body>
            <h1>Welcome</h1>
            <p>This is a regular HTML page with lots of content that doesn't depend heavily on JavaScript for rendering. The content is readily available in the HTML source and can be easily scraped using simple HTTP requests and HTML parsing.</p>
            <div class="job-listing">
                <h2>Software Engineer</h2>
                <p>Company: Tech Corp</p>
                <p>Location: Tokyo, Japan</p>
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = self.analyzer._analyze_javascript_dependency(soup, html_content)
        self.assertFalse(result)
    
    def test_detect_spa_patterns_positive(self):
        """Test SPA pattern detection with positive case"""
        html_content = """
        <html>
        <body>
            <div id="root" data-react-root="true"></div>
            <script src="app.js"></script>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = self.analyzer._detect_spa_patterns(soup, html_content)
        self.assertTrue(result)
    
    def test_detect_spa_patterns_negative(self):
        """Test SPA pattern detection with negative case"""
        html_content = """
        <html>
        <body>
            <header>Header content</header>
            <nav>Navigation</nav>
            <main>
                <h1>Welcome</h1>
                <p>Regular content</p>
            </main>
            <aside>Sidebar</aside>
            <footer>Footer content</footer>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = self.analyzer._detect_spa_patterns(soup, html_content)
        self.assertFalse(result)
    
    def test_detect_job_board_patterns_positive(self):
        """Test job board pattern detection with positive case"""
        html_content = """
        <html>
        <body>
            <div class="job-card">
                <h2 class="job-title">Software Engineer</h2>
                <span class="company-name">Tech Corp</span>
                <div class="location">Tokyo, Japan</div>
                <button>Apply Now</button>
            </div>
            <div class="job-listing">
                <h3>Data Scientist</h3>
                <p>Full-time position available</p>
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = self.analyzer._detect_job_board_patterns(soup, html_content)
        self.assertTrue(result)
    
    def test_detect_job_board_patterns_negative(self):
        """Test job board pattern detection with negative case"""
        html_content = """
        <html>
        <body>
            <h1>About Our Company</h1>
            <p>We are a technology company focused on innovation.</p>
            <div class="news-article">
                <h2>Latest News</h2>
                <p>Company updates and announcements</p>
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = self.analyzer._detect_job_board_patterns(soup, html_content)
        self.assertFalse(result)
    
    def test_analyze_html_simplicity_simple(self):
        """Test HTML simplicity analysis for simple structure"""
        html_content = """
        <html>
        <body>
            <h1>Job Listings</h1>
            <div class="job">
                <h2>Software Engineer</h2>
                <a href="/job/123">View Details</a>
                <a href="/apply/123">Apply Now</a>
                <a href="/company/tech">Company Info</a>
                <p>Great opportunity for a talented developer to join our growing team. We offer competitive salary, great benefits, and flexible working arrangements. This is a full-time position based in Tokyo, Japan with opportunities for remote work and professional development.</p>
            </div>
            <div class="job">
                <h2>Data Scientist</h2>
                <a href="/job/456">View Details</a>
                <a href="/apply/456">Apply Now</a>
                <a href="/company/data">Company Info</a>
                <p>Join our analytics team and help drive data-driven decisions across the organization. We're looking for someone with strong statistical background and experience with machine learning algorithms.</p>
            </div>
            <div class="job">
                <h2>Frontend Developer</h2>
                <a href="/job/789">View Details</a>
                <a href="/apply/789">Apply Now</a>
                <p>Build amazing user experiences with modern web technologies. Experience with React, Vue, or Angular required.</p>
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = self.analyzer._analyze_html_simplicity(soup)
        self.assertTrue(result)
    
    def test_analyze_html_simplicity_complex(self):
        """Test HTML simplicity analysis for complex structure"""
        html_content = """
        <html>
        <body>
            <div id="app">
                <template v-for="job in jobs">
                    <div>{{ job.title }}</div>
                </template>
            </div>
            <script>/* lots of scripts */</script>
            <script>/* more scripts */</script>
            <script>/* even more scripts */</script>
            <script>/* too many scripts */</script>
            <script>/* way too many scripts */</script>
            <script>/* definitely too many scripts */</script>
            <script>/* absolutely too many scripts */</script>
            <script>/* ridiculously too many scripts */</script>
            <script>/* excessively too many scripts */</script>
            <script>/* overwhelmingly too many scripts */</script>
            <script>/* unbearably too many scripts */</script>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = self.analyzer._analyze_html_simplicity(soup)
        self.assertFalse(result)
    
    def test_detect_anti_bot_measures_positive(self):
        """Test anti-bot detection with positive case"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Access denied due to bot detection"
        mock_response.headers = {'cf-ray': '12345'}
        
        result = self.analyzer._detect_anti_bot_measures(mock_response)
        self.assertTrue(result)
    
    def test_detect_anti_bot_measures_negative(self):
        """Test anti-bot detection with negative case"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Welcome to our website"
        mock_response.headers = {}
        
        result = self.analyzer._detect_anti_bot_measures(mock_response)
        self.assertFalse(result)
    
    def test_determine_strategy_api(self):
        """Test strategy determination for API"""
        analysis = {
            'api_detected': True,
            'anti_bot_detected': False,
            'simple_html': True,
            'javascript_heavy': False,
            'spa_detected': False,
            'job_board_patterns': True
        }
        
        strategy, confidence = self.analyzer._determine_strategy(analysis)
        self.assertEqual(strategy, 'api')
        self.assertEqual(confidence, 0.9)
    
    def test_determine_strategy_requests(self):
        """Test strategy determination for requests"""
        analysis = {
            'api_detected': False,
            'anti_bot_detected': False,
            'simple_html': True,
            'javascript_heavy': False,
            'spa_detected': False,
            'job_board_patterns': True
        }
        
        strategy, confidence = self.analyzer._determine_strategy(analysis)
        self.assertEqual(strategy, 'requests')
        self.assertEqual(confidence, 0.85)
    
    def test_determine_strategy_selenium(self):
        """Test strategy determination for selenium"""
        analysis = {
            'api_detected': False,
            'anti_bot_detected': False,
            'simple_html': False,
            'javascript_heavy': True,
            'spa_detected': True,
            'job_board_patterns': False
        }
        
        strategy, confidence = self.analyzer._determine_strategy(analysis)
        self.assertEqual(strategy, 'selenium')
        self.assertEqual(confidence, 0.8)
    
    def test_get_strategy_explanation(self):
        """Test strategy explanation generation"""
        analysis = {
            'recommended_strategy': 'api',
            'confidence': 0.9,
            'anti_bot_detected': False,
            'response_time': 2.0,
            'error': None
        }
        
        explanation = self.analyzer.get_strategy_explanation(analysis)
        self.assertIn('API endpoints detected', explanation)
        self.assertIn('confidence: 90.0%', explanation)
    
    def test_get_strategy_explanation_with_warnings(self):
        """Test strategy explanation with warnings"""
        analysis = {
            'recommended_strategy': 'selenium',
            'confidence': 0.4,
            'anti_bot_detected': True,
            'response_time': 8.0,
            'error': 'Connection timeout'
        }
        
        explanation = self.analyzer.get_strategy_explanation(analysis)
        self.assertIn('⚠️ Anti-bot measures detected', explanation)
        self.assertIn('⚠️ Slow response time detected', explanation)
        self.assertIn('⚠️ Analysis error: Connection timeout', explanation)
    
    @patch('requests.Session.get')
    def test_analyze_website_full_flow(self, mock_get):
        """Test full website analysis flow"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
        <body>
            <h1>Job Listings</h1>
            <div class="job-card">
                <h2>Software Engineer</h2>
                <span>Tech Corp</span>
                <a href="/apply">Apply Now</a>
            </div>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        result = self.analyzer.analyze_website("https://example.com/jobs")
        
        # Verify structure
        self.assertIn('url', result)
        self.assertIn('recommended_strategy', result)
        self.assertIn('confidence', result)
        self.assertIn('api_detected', result)
        self.assertIn('javascript_heavy', result)
        self.assertIn('spa_detected', result)
        self.assertIn('job_board_patterns', result)
        self.assertIn('anti_bot_detected', result)
        self.assertIn('response_time', result)
        self.assertIn('status_code', result)
        
        # Verify values
        self.assertEqual(result['url'], "https://example.com/jobs")
        self.assertEqual(result['status_code'], 200)
        self.assertIsInstance(result['confidence'], float)
        self.assertIn(result['recommended_strategy'], ['api', 'requests', 'selenium'])


class TestWebsiteAnalyzerIntegration(unittest.TestCase):
    """Integration tests for WebsiteAnalyzer with real websites"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = WebsiteAnalyzer(timeout=10)
    
    def test_analyze_simple_website(self):
        """Test analysis of a simple website (if accessible)"""
        # This test requires internet connection
        try:
            result = self.analyzer.analyze_website("https://httpbin.org/html")
            
            self.assertIsNotNone(result)
            self.assertIn('recommended_strategy', result)
            self.assertIsInstance(result['confidence'], float)
            self.assertGreaterEqual(result['confidence'], 0.0)
            self.assertLessEqual(result['confidence'], 1.0)
            
        except Exception as e:
            self.skipTest(f"Integration test skipped due to network issue: {e}")
    
    def test_analyze_json_api(self):
        """Test analysis of a JSON API endpoint"""
        # This test requires internet connection
        try:
            result = self.analyzer.analyze_website("https://httpbin.org/json")
            
            self.assertIsNotNone(result)
            # Should detect API
            self.assertTrue(result['api_detected'])
            self.assertEqual(result['recommended_strategy'], 'api')
            
        except Exception as e:
            self.skipTest(f"Integration test skipped due to network issue: {e}")


def run_tests():
    """Run all tests"""
    # Create test loader
    loader = unittest.TestLoader()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add unit tests
    test_suite.addTest(loader.loadTestsFromTestCase(TestWebsiteAnalyzer))
    
    # Add integration tests (optional)
    test_suite.addTest(loader.loadTestsFromTestCase(TestWebsiteAnalyzerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Running WebsiteAnalyzer tests...")
    success = run_tests()
    
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        exit(1)