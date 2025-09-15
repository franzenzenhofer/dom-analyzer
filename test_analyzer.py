"""
Comprehensive Unit Tests for DOM Analyzer Core Functions
Tests all major functions with edge cases, mocks, and performance validation
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import responses
from bs4 import BeautifulSoup
import time
import json
from typing import Dict, Any

from core_analyzer import CoreDOMAnalyzer, LegacyDOMAnalyzer
from test_fixtures import (
    MockHTMLFixtures, 
    MockResponseFixtures, 
    TestURLs, 
    ExpectedResults,
    ValidationHelpers,
    TestDataGenerator,
    setup_mock_responses
)


class TestCoreDOMAnalyzer(unittest.TestCase):
    """Test CoreDOMAnalyzer class methods"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_url = 'https://example.com'
        self.analyzer = CoreDOMAnalyzer(self.test_url)
        self.simple_soup = BeautifulSoup(MockHTMLFixtures.SIMPLE_HTML, 'html.parser')
        self.complex_soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
        
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization with various URLs"""
        # Valid URL
        analyzer = CoreDOMAnalyzer('https://example.com')
        self.assertEqual(analyzer.url, 'https://example.com')
        self.assertEqual(analyzer.parsed_url.netloc, 'example.com')
        self.assertEqual(analyzer.base_domain, 'example.com')
        
        # URL with subdomain
        analyzer = CoreDOMAnalyzer('https://www.subdomain.example.com/path')
        self.assertEqual(analyzer.base_domain, 'example.com')
        
        # Custom timeout and SSL settings
        analyzer = CoreDOMAnalyzer('https://test.com', timeout=60, verify_ssl=True)
        self.assertEqual(analyzer.timeout, 60)
        self.assertTrue(analyzer.verify_ssl)
    
    @responses.activate
    def test_fetch_single_user_agent_success(self):
        """Test successful single user agent fetch"""
        responses.add(
            responses.GET,
            self.test_url,
            body=MockHTMLFixtures.SIMPLE_HTML,
            status=200,
            headers={'Content-Type': 'text/html'}
        )
        
        result = self.analyzer.fetch_single_user_agent('desktop_chrome')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['status_code'], 200)
        self.assertIn('html', result)
        self.assertIn('soup', result)
        self.assertGreater(result['content_length'], 0)
        self.assertIsInstance(result['soup'], BeautifulSoup)
    
    @responses.activate
    def test_fetch_single_user_agent_failure(self):
        """Test fetch failure handling"""
        responses.add(
            responses.GET,
            self.test_url,
            status=404
        )
        
        result = self.analyzer.fetch_single_user_agent('desktop_chrome')
        
        self.assertIsNone(result)
        self.assertIn('desktop_chrome', self.analyzer.responses)
        self.assertIn('error', self.analyzer.responses['desktop_chrome'])
    
    @responses.activate 
    def test_fetch_all_user_agents(self):
        """Test fetching with all user agents"""
        # Mock successful response for all user agents
        for ua_name in CoreDOMAnalyzer.USER_AGENTS.keys():
            responses.add(
                responses.GET,
                self.test_url,
                body=MockHTMLFixtures.SIMPLE_HTML,
                status=200,
                headers={'Content-Type': 'text/html'}
            )
        
        results = self.analyzer.fetch_with_all_user_agents()
        
        self.assertEqual(len(results), len(CoreDOMAnalyzer.USER_AGENTS))
        
        # Check that all user agents were tested
        for ua_name in CoreDOMAnalyzer.USER_AGENTS.keys():
            self.assertIn(ua_name, results)
            if 'error' not in results[ua_name]:
                self.assertIn('status_code', results[ua_name])
                self.assertIn('soup', results[ua_name])
    
    def test_calculate_dom_complexity_simple(self):
        """Test DOM complexity calculation with simple HTML"""
        result = self.analyzer.calculate_dom_complexity(self.simple_soup)
        
        self.assertIsInstance(result, dict)
        self.assertIn('total_elements', result)
        self.assertIn('max_depth', result)
        self.assertIn('leaf_nodes', result)
        self.assertIn('branch_nodes', result)
        self.assertIn('complexity_score', result)
        
        # Validate specific values for simple HTML
        self.assertGreaterEqual(result['total_elements'], 5)
        self.assertGreaterEqual(result['max_depth'], 2)
        self.assertGreater(result['complexity_score'], 0)
    
    def test_calculate_dom_complexity_complex(self):
        """Test DOM complexity calculation with complex HTML"""
        result = self.analyzer.calculate_dom_complexity(self.complex_soup)
        
        # Complex HTML should have more elements and deeper nesting
        self.assertGreater(result['total_elements'], 20)
        self.assertGreater(result['max_depth'], 3)
        self.assertGreater(result['complexity_score'], 100)
    
    def test_calculate_dom_complexity_empty(self):
        """Test DOM complexity with empty HTML"""
        empty_soup = BeautifulSoup(MockHTMLFixtures.EMPTY_HTML, 'html.parser')
        result = self.analyzer.calculate_dom_complexity(empty_soup)
        
        self.assertGreaterEqual(result['total_elements'], 0)
        self.assertGreaterEqual(result['max_depth'], 0)
    
    def test_analyze_css_selectors(self):
        """Test CSS selector analysis"""
        result = self.analyzer.analyze_css_selectors(self.complex_soup)
        
        required_keys = ['unique_ids', 'unique_classes', 'bem_score', 'atomic_css_score', 'inline_styles']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Complex HTML should have CSS classes and IDs
        self.assertGreater(result['unique_classes'], 0)
        self.assertGreaterEqual(result['inline_styles'], 0)
    
    def test_analyze_css_selectors_bem_detection(self):
        """Test BEM methodology detection in CSS"""
        bem_html = """
        <html>
        <body>
            <div class="block">
                <div class="block__element">
                    <div class="block__element--modifier">BEM Test</div>
                </div>
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(bem_html, 'html.parser')
        result = self.analyzer.analyze_css_selectors(soup)
        
        self.assertGreater(result['bem_score'], 0)
    
    def test_analyze_javascript_complexity(self):
        """Test JavaScript complexity analysis"""
        result = self.analyzer.analyze_javascript_complexity(self.complex_soup)
        
        required_keys = ['total_scripts', 'inline_scripts', 'external_scripts', 'frameworks_detected']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Complex HTML has both inline and external scripts
        self.assertGreater(result['total_scripts'], 0)
        self.assertGreater(result['inline_scripts'], 0)
        self.assertGreater(result['external_scripts'], 0)
        
        # Should detect jQuery
        self.assertIn('jquery', result['frameworks_detected'])
    
    def test_analyze_javascript_modern_patterns(self):
        """Test detection of modern JavaScript patterns"""
        result = self.analyzer.analyze_javascript_complexity(self.complex_soup)
        
        # Should detect modern JS patterns in complex HTML
        patterns = result.get('patterns', {})
        self.assertIn('arrow_functions', patterns)
        self.assertIn('class_syntax', patterns)
        self.assertIn('async_await_usage', result)
        self.assertIn('promise_usage', result)
        
        # Values should be positive for complex HTML with modern JS
        self.assertGreater(result['async_await_usage'], 0)
        self.assertGreater(result['promise_usage'], 0)
    
    def test_analyze_performance_metrics(self):
        """Test performance metrics analysis"""
        mock_response = {'content_length': 50000, 'response_time': 0.5}
        result = self.analyzer.analyze_performance_metrics(self.complex_soup, mock_response)
        
        required_sections = ['lazy_loading', 'image_optimization', 'resource_hints', 'service_worker']
        for section in required_sections:
            self.assertIn(section, result)
        
        # Complex HTML should have resource hints and lazy loading
        self.assertGreater(result['resource_hints']['preconnect'].__len__(), 0)
        self.assertGreater(result['lazy_loading']['images'], 0)
        self.assertTrue(result['service_worker'])  # Complex HTML registers SW
    
    def test_analyze_seo_signals_comprehensive(self):
        """Test comprehensive SEO analysis"""
        result = self.analyzer.analyze_seo_signals(self.complex_soup)
        
        # Title analysis
        title = result['title']
        self.assertTrue(title['exists'])
        self.assertGreater(title['length'], 0)
        self.assertIsInstance(title['optimal'], bool)
        
        # Meta description
        meta_desc = result['meta_tags']['description']
        self.assertTrue(meta_desc['exists'])
        self.assertGreater(meta_desc['length'], 0)
        
        # Schema.org
        schema = result['schema_org']
        self.assertEqual(schema['json_ld_count'], 1)
        self.assertIn('WebPage', schema['types'])
        
        # Open Graph
        og = result['open_graph']
        self.assertGreater(og['count'], 0)
        self.assertIn('og:title', og['properties'])
        
        # Content quality
        content = result['content_quality']
        self.assertGreater(content['word_count'], 50)
        self.assertGreater(content['paragraph_count'], 0)
    
    def test_analyze_seo_signals_issues(self):
        """Test SEO analysis with problematic content"""
        issues_soup = BeautifulSoup(MockHTMLFixtures.SEO_ISSUES_HTML, 'html.parser')
        result = self.analyzer.analyze_seo_signals(issues_soup)
        
        # Should detect long title
        title = result['title']
        self.assertFalse(title['optimal'])  # Too long
        
        # Should detect short meta description
        meta_desc = result['meta_tags']['description']
        self.assertFalse(meta_desc['optimal'])  # Too short
        
        # Should detect multiple H1s
        self.assertFalse(result['headings']['has_single_h1'])
    
    def test_analyze_accessibility_advanced(self):
        """Test advanced accessibility analysis"""
        result = self.analyzer.analyze_accessibility_advanced(self.complex_soup)
        
        # ARIA usage
        aria = result['aria']
        self.assertIn('aria-label', aria)
        self.assertIn('aria-labelledby', aria)
        
        # Semantic HTML
        semantic = result['semantic_html']
        self.assertIn('header', semantic)
        self.assertIn('main', semantic)
        self.assertIn('nav', semantic)
        self.assertIn('footer', semantic)
        
        # Form labels
        form_labels = result['form_labels']
        self.assertGreater(form_labels['inputs_with_labels'], 0)
        self.assertEqual(form_labels['inputs_without_labels'], 1)  # Phone input missing label
        
        # Images and alt text
        alt_text = result['alternative_text']
        self.assertGreater(alt_text['total_images'], 0)
        self.assertGreater(alt_text['with_alt'], 0)
        self.assertEqual(alt_text['missing_alt'], 1)  # One image without alt
        
        # Skip navigation
        skip_nav = result['skip_navigation']
        self.assertTrue(skip_nav['exists'])
        self.assertGreater(skip_nav['count'], 0)
        
        # Language
        lang = result['language']
        self.assertEqual(lang['html_lang'], 'en')
    
    def test_analyze_accessibility_issues(self):
        """Test accessibility analysis with known issues"""
        issues_soup = BeautifulSoup(MockHTMLFixtures.ACCESSIBILITY_ISSUES_HTML, 'html.parser')
        result = self.analyzer.analyze_accessibility_advanced(issues_soup)
        
        # Should detect missing alt text
        alt_text = result['alternative_text']
        self.assertGreater(alt_text['missing_alt'], 0)
        
        # Should detect form inputs without labels
        form_labels = result['form_labels']
        self.assertGreater(form_labels['inputs_without_labels'], 0)
        
        # Should detect missing language attribute
        lang = result['language']
        self.assertIsNone(lang['html_lang'])
    
    def test_analyze_security_headers(self):
        """Test security headers analysis"""
        # Test with good security headers
        good_headers = MockResponseFixtures.get_security_headers()
        result = self.analyzer.analyze_security_headers(good_headers)
        
        self.assertGreater(result['security_score'], 80)
        self.assertIn('Strict-Transport-Security', result['headers_present'])
        self.assertIn('Content-Security-Policy', result['headers_present'])
        
        # CSP analysis
        csp = result['csp']
        self.assertTrue(csp['present'])
        self.assertTrue(csp['default_src'])
        
        # Cookie analysis
        cookies = result['cookies']
        self.assertTrue(cookies['present'])
        self.assertTrue(cookies['secure'])
        self.assertTrue(cookies['httponly'])
        
        # Test with minimal headers
        minimal_headers = MockResponseFixtures.get_minimal_headers()
        result_minimal = self.analyzer.analyze_security_headers(minimal_headers)
        
        self.assertLess(result_minimal['security_score'], 20)
        self.assertEqual(len(result_minimal['headers_present']), 0)
    
    @patch('time.time')
    def test_count_total_statistics(self, mock_time):
        """Test statistics counting"""
        test_data = {
            'section1': {
                'subsection1': {'key1': 'value1', 'key2': 'value2'},
                'subsection2': ['item1', 'item2', 'item3']
            },
            'section2': {
                'count': 42,
                'enabled': True
            }
        }
        
        count = self.analyzer.count_total_statistics(test_data)
        self.assertGreater(count, 10)  # Should count all nested items
    
    @responses.activate
    def test_generate_comprehensive_analysis(self):
        """Test complete analysis pipeline"""
        responses.add(
            responses.GET,
            self.test_url,
            body=MockHTMLFixtures.COMPLEX_HTML,
            status=200,
            headers=MockResponseFixtures.get_security_headers()
        )
        
        result = self.analyzer.generate_comprehensive_analysis()
        
        # Should not have error
        self.assertNotIn('error', result)
        
        # Should have all analysis sections
        expected_sections = [
            'url', 'user_agent_used', 'fetch_info', 'dom_complexity',
            'css_analysis', 'javascript_analysis', 'performance_metrics',
            'seo_signals', 'accessibility', 'security', 'meta_statistics'
        ]
        
        for section in expected_sections:
            self.assertIn(section, result, f"Missing section: {section}")
        
        # Validate fetch info
        fetch_info = result['fetch_info']
        self.assertEqual(fetch_info['status_code'], 200)
        self.assertGreater(fetch_info['content_length'], 0)
        
        # Validate meta statistics
        meta = result['meta_statistics']
        self.assertGreater(meta['total_data_points'], 100)
        self.assertGreater(meta['processing_time'], 0)
        self.assertIn('timestamp', meta)
    
    @responses.activate
    def test_generate_comprehensive_analysis_error(self):
        """Test analysis with fetch error"""
        responses.add(
            responses.GET,
            self.test_url,
            status=404
        )
        
        result = self.analyzer.generate_comprehensive_analysis()
        
        self.assertIn('error', result)
        self.assertIn('Failed to fetch page', result['error'])


class TestLegacyDOMAnalyzer(unittest.TestCase):
    """Test backward compatibility wrapper"""
    
    def setUp(self):
        self.test_url = 'https://example.com'
        self.analyzer = LegacyDOMAnalyzer(self.test_url)
    
    @responses.activate
    def test_legacy_analyze_method(self):
        """Test legacy analyze method compatibility"""
        responses.add(
            responses.GET,
            self.test_url,
            body=MockHTMLFixtures.SIMPLE_HTML,
            status=200,
            headers={'Content-Type': 'text/html'}
        )
        
        result = self.analyzer.analyze()
        
        self.assertIsNotNone(result)
        self.assertIn('url', result)
        self.assertIn('assets', result)
        self.assertIn('domain_stats', result)
        self.assertIn('statistics', result)
    
    def test_categorize_domain(self):
        """Test domain categorization"""
        # Same origin
        category, url = self.analyzer.categorize_domain('/local/resource.js')
        self.assertEqual(category, 'same_origin')
        
        # Third party
        category, url = self.analyzer.categorize_domain('https://external.com/resource.js')
        self.assertEqual(category, 'third_party')
        
        # Subdomain
        category, url = self.analyzer.categorize_domain('https://cdn.example.com/resource.js')
        self.assertEqual(category, 'subdomain')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        self.test_url = 'https://example.com'
        self.analyzer = CoreDOMAnalyzer(self.test_url)
    
    def test_malformed_html_handling(self):
        """Test handling of malformed HTML"""
        malformed_soup = BeautifulSoup(MockHTMLFixtures.MALFORMED_HTML, 'html.parser')
        
        # Should not crash with malformed HTML
        dom_result = self.analyzer.calculate_dom_complexity(malformed_soup)
        self.assertIsInstance(dom_result, dict)
        self.assertIn('total_elements', dom_result)
        
        css_result = self.analyzer.analyze_css_selectors(malformed_soup)
        self.assertIsInstance(css_result, dict)
        
        js_result = self.analyzer.analyze_javascript_complexity(malformed_soup)
        self.assertIsInstance(js_result, dict)
    
    def test_empty_html_handling(self):
        """Test handling of empty HTML"""
        empty_soup = BeautifulSoup(MockHTMLFixtures.EMPTY_HTML, 'html.parser')
        
        seo_result = self.analyzer.analyze_seo_signals(empty_soup)
        self.assertFalse(seo_result['title']['exists'])
        
        accessibility_result = self.analyzer.analyze_accessibility_advanced(empty_soup)
        self.assertEqual(accessibility_result['alternative_text']['total_images'], 0)
    
    def test_no_doctype_handling(self):
        """Test handling of HTML without DOCTYPE"""
        no_doctype_soup = BeautifulSoup(MockHTMLFixtures.NO_DOCTYPE_HTML, 'html.parser')
        
        # Should still analyze without issues
        result = self.analyzer.calculate_dom_complexity(no_doctype_soup)
        self.assertGreater(result['total_elements'], 0)
    
    def test_invalid_json_ld(self):
        """Test handling of invalid JSON-LD structured data"""
        invalid_json_html = '''
        <html>
        <head>
            <script type="application/ld+json">
            { invalid json content
            </script>
        </head>
        <body><p>Test</p></body>
        </html>
        '''
        soup = BeautifulSoup(invalid_json_html, 'html.parser')
        result = self.analyzer.analyze_seo_signals(soup)
        
        # Should handle invalid JSON gracefully
        self.assertEqual(result['schema_org']['json_ld_count'], 1)
        self.assertEqual(len(result['schema_org']['types']), 0)
    
    def test_extreme_nesting(self):
        """Test with extremely deep HTML nesting"""
        deep_html = TestDataGenerator.generate_deep_nested_html(50)
        deep_soup = BeautifulSoup(deep_html, 'html.parser')
        
        result = self.analyzer.calculate_dom_complexity(deep_soup)
        self.assertGreaterEqual(result['max_depth'], 50)
        self.assertGreater(result['complexity_score'], 1000)
    
    def test_many_elements_performance(self):
        """Test performance with many elements"""
        start_time = time.time()
        
        large_html = TestDataGenerator.generate_large_html(500)
        large_soup = BeautifulSoup(large_html, 'html.parser')
        
        result = self.analyzer.calculate_dom_complexity(large_soup)
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        # Should complete analysis in reasonable time
        self.assertLess(analysis_time, 5.0)  # Less than 5 seconds
        self.assertGreater(result['total_elements'], 500)
    
    def test_unicode_content_handling(self):
        """Test handling of Unicode content"""
        unicode_html = '''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <title>测试页面</title>
            <meta name="description" content="这是一个包含中文内容的测试页面">
        </head>
        <body>
            <h1>欢迎</h1>
            <p>这是一些中文内容，包含表情符号 😀🎉</p>
            <p>العربية والإنجليزية</p>
            <p>Русский текст</p>
        </body>
        </html>
        '''
        
        unicode_soup = BeautifulSoup(unicode_html, 'html.parser')
        result = self.analyzer.analyze_seo_signals(unicode_soup)
        
        # Should handle Unicode properly
        self.assertEqual(result['title']['text'], '测试页面')
        self.assertIn('这是一个包含中文', result['meta_tags']['description']['content'])
        self.assertGreater(result['content_quality']['word_count'], 0)


class TestPerformance(unittest.TestCase):
    """Performance and benchmark tests"""
    
    def setUp(self):
        self.test_url = 'https://example.com'
        self.analyzer = CoreDOMAnalyzer(self.test_url)
    
    def test_analysis_performance_simple(self):
        """Test analysis performance with simple content"""
        simple_soup = BeautifulSoup(MockHTMLFixtures.SIMPLE_HTML, 'html.parser')
        
        start_time = time.time()
        
        # Run all analyses
        self.analyzer.calculate_dom_complexity(simple_soup)
        self.analyzer.analyze_css_selectors(simple_soup)
        self.analyzer.analyze_javascript_complexity(simple_soup)
        self.analyzer.analyze_seo_signals(simple_soup)
        self.analyzer.analyze_accessibility_advanced(simple_soup)
        
        total_time = time.time() - start_time
        
        # Should be fast for simple content
        self.assertLess(total_time, 1.0)
    
    def test_analysis_performance_complex(self):
        """Test analysis performance with complex content"""
        complex_soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
        
        start_time = time.time()
        
        # Run all analyses
        self.analyzer.calculate_dom_complexity(complex_soup)
        self.analyzer.analyze_css_selectors(complex_soup)
        self.analyzer.analyze_javascript_complexity(complex_soup)
        self.analyzer.analyze_seo_signals(complex_soup)
        self.analyzer.analyze_accessibility_advanced(complex_soup)
        
        total_time = time.time() - start_time
        
        # Should complete within reasonable time
        self.assertLess(total_time, 5.0)
    
    def test_memory_usage_large_content(self):
        """Test memory usage with large content"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate and analyze large content
        large_html = TestDataGenerator.generate_large_html(1000)
        large_soup = BeautifulSoup(large_html, 'html.parser')
        
        result = self.analyzer.calculate_dom_complexity(large_soup)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        # Should not use excessive memory
        self.assertLess(memory_used, 100)  # Less than 100MB additional


if __name__ == '__main__':
    # Set up mock responses
    setup_mock_responses()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCoreDOMAnalyzer,
        TestLegacyDOMAnalyzer,
        TestEdgeCases,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")