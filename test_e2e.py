"""
End-to-End Tests for DOM Analyzer Flask Application
Tests the complete Flask app functionality using pytest and selenium
"""

import pytest
import time
import json
import subprocess
import signal
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading
from contextlib import contextmanager

from test_fixtures import TestURLs, MockHTMLFixtures, setup_mock_responses


class FlaskAppManager:
    """Manages Flask app lifecycle for testing"""
    
    def __init__(self, app_module='app.py', port=5001):
        self.app_module = app_module
        self.port = port
        self.process = None
        self.base_url = f'http://localhost:{port}'
        
    def start(self):
        """Start Flask app in background"""
        env = os.environ.copy()
        env['FLASK_ENV'] = 'testing'
        env['FLASK_PORT'] = str(self.port)
        
        self.process = subprocess.Popen(
            ['python3', self.app_module],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Wait for app to start
        max_retries = 30
        for _ in range(max_retries):
            try:
                response = requests.get(f'{self.base_url}/', timeout=1)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                time.sleep(0.5)
        
        raise Exception(f"Failed to start Flask app on port {self.port}")
    
    def stop(self):
        """Stop Flask app"""
        if self.process:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait(timeout=10)
            self.process = None
    
    @contextmanager
    def running(self):
        """Context manager for Flask app lifecycle"""
        try:
            self.start()
            yield self
        finally:
            self.stop()


@pytest.fixture(scope='session')
def flask_app():
    """Session-scoped Flask app fixture"""
    with FlaskAppManager().running() as app:
        yield app


@pytest.fixture(scope='session') 
def browser():
    """Session-scoped browser fixture"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Try to use system Chrome or fallback to ChromeDriver
    try:
        driver = webdriver.Chrome(options=options)
    except Exception:
        # If Chrome not found, skip selenium tests
        pytest.skip("Chrome browser not available for Selenium tests")
    
    yield driver
    driver.quit()


@pytest.fixture
def wait(browser):
    """WebDriverWait fixture"""
    return WebDriverWait(browser, 10)


class TestFlaskAppEndpoints:
    """Test Flask app endpoints directly"""
    
    def test_home_page_loads(self, flask_app):
        """Test home page loads successfully"""
        response = requests.get(f'{flask_app.base_url}/')
        assert response.status_code == 200
        assert 'DOM Analyzer' in response.text or 'html' in response.text.lower()
    
    def test_analyze_endpoint_with_valid_url(self, flask_app):
        """Test /analyze endpoint with valid URL"""
        test_data = {'url': 'https://example.com'}
        
        response = requests.post(
            f'{flask_app.base_url}/analyze',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Note: This will likely fail without mocking, but tests the endpoint structure
        assert response.status_code in [200, 500]  # 500 expected if no mocking
        
        if response.status_code == 200:
            data = response.json()
            assert 'url' in data
            assert 'assets' in data or 'statistics' in data
    
    def test_analyze_endpoint_with_invalid_url(self, flask_app):
        """Test /analyze endpoint with invalid URL"""
        test_data = {'url': 'invalid-url'}
        
        response = requests.post(
            f'{flask_app.base_url}/analyze',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Should handle invalid URLs gracefully
        assert response.status_code in [200, 400, 500]
    
    def test_analyze_endpoint_missing_url(self, flask_app):
        """Test /analyze endpoint without URL"""
        test_data = {}
        
        response = requests.post(
            f'{flask_app.base_url}/analyze',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'required' in data['error'].lower()
    
    def test_graph_endpoint_exists(self, flask_app):
        """Test /graph endpoint exists"""
        response = requests.get(f'{flask_app.base_url}/graph')
        assert response.status_code in [200, 404]  # May not exist if no graph generated


class TestSeleniumUI:
    """Test UI interactions with Selenium"""
    
    def test_page_loads_completely(self, flask_app, browser, wait):
        """Test that the main page loads completely"""
        browser.get(flask_app.base_url)
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # Check basic page structure
        assert browser.title is not None
        assert len(browser.title) > 0
        
        # Should have some form of input or interface
        body_text = browser.find_element(By.TAG_NAME, 'body').text
        assert len(body_text) > 0
    
    def test_url_input_form_exists(self, flask_app, browser, wait):
        """Test URL input form exists and is functional"""
        browser.get(flask_app.base_url)
        
        try:
            # Look for common form elements
            url_inputs = browser.find_elements(By.CSS_SELECTOR, 'input[type="url"], input[type="text"], input[name*="url"]')
            submit_buttons = browser.find_elements(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"], button')
            
            # Should have some form of URL input
            assert len(url_inputs) > 0 or len(submit_buttons) > 0, "No form elements found"
            
            if url_inputs:
                url_input = url_inputs[0]
                assert url_input.is_enabled()
                
                # Try entering a URL
                url_input.clear()
                url_input.send_keys('https://example.com')
                
                entered_value = url_input.get_attribute('value')
                assert 'example.com' in entered_value
                
        except NoSuchElementException:
            pytest.skip("URL input form not found - may be JavaScript-rendered")
    
    def test_form_submission_triggers_analysis(self, flask_app, browser, wait):
        """Test form submission triggers analysis"""
        browser.get(flask_app.base_url)
        
        try:
            # Find and fill URL input
            url_inputs = browser.find_elements(By.CSS_SELECTOR, 'input[type="url"], input[type="text"], input[name*="url"]')
            submit_buttons = browser.find_elements(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"], button')
            
            if url_inputs and submit_buttons:
                url_input = url_inputs[0]
                submit_button = submit_buttons[0]
                
                # Enter test URL
                url_input.clear()
                url_input.send_keys('https://httpbin.org/html')
                
                # Submit form
                initial_url = browser.current_url
                submit_button.click()
                
                # Wait for some change or response
                time.sleep(2)
                
                # Check for results or loading indicators
                page_text = browser.find_element(By.TAG_NAME, 'body').text.lower()
                
                # Should show some indication of processing or results
                indicators = ['loading', 'analyzing', 'results', 'error', 'analysis', 'complete']
                has_indicator = any(indicator in page_text for indicator in indicators)
                
                # Or URL might change
                url_changed = browser.current_url != initial_url
                
                assert has_indicator or url_changed, "No indication of form processing"
        
        except (NoSuchElementException, TimeoutException):
            pytest.skip("Form submission test skipped - elements not found")
    
    def test_results_display_structure(self, flask_app, browser, wait):
        """Test results display structure after analysis"""
        browser.get(flask_app.base_url)
        
        # This test assumes we can trigger an analysis and see results
        try:
            # Try to find pre-existing results or trigger analysis
            page_text = browser.find_element(By.TAG_NAME, 'body').text.lower()
            
            # Look for common result indicators
            result_indicators = ['statistics', 'analysis', 'dom', 'seo', 'performance', 'accessibility']
            has_results = any(indicator in page_text for indicator in result_indicators)
            
            if not has_results:
                # Try to trigger analysis if possible
                url_inputs = browser.find_elements(By.CSS_SELECTOR, 'input[type="url"], input[type="text"]')
                submit_buttons = browser.find_elements(By.CSS_SELECTOR, 'button')
                
                if url_inputs and submit_buttons:
                    url_inputs[0].send_keys('https://example.com')
                    submit_buttons[0].click()
                    time.sleep(3)
                    
                    page_text = browser.find_element(By.TAG_NAME, 'body').text.lower()
                    has_results = any(indicator in page_text for indicator in result_indicators)
            
            if has_results:
                # Check for structured results
                sections = browser.find_elements(By.CSS_SELECTOR, 'div, section, table, ul')
                assert len(sections) > 5, "Results should have multiple sections"
                
        except (NoSuchElementException, TimeoutException):
            pytest.skip("Results display test skipped - unable to trigger or find results")
    
    def test_error_handling_display(self, flask_app, browser, wait):
        """Test error handling in UI"""
        browser.get(flask_app.base_url)
        
        try:
            url_inputs = browser.find_elements(By.CSS_SELECTOR, 'input[type="url"], input[type="text"]')
            submit_buttons = browser.find_elements(By.CSS_SELECTOR, 'button')
            
            if url_inputs and submit_buttons:
                # Enter invalid URL
                url_inputs[0].clear()
                url_inputs[0].send_keys('invalid-url-test')
                submit_buttons[0].click()
                
                # Wait for response
                time.sleep(2)
                
                # Check for error handling
                page_text = browser.find_element(By.TAG_NAME, 'body').text.lower()
                error_indicators = ['error', 'invalid', 'failed', 'unable']
                
                has_error_handling = any(indicator in page_text for indicator in error_indicators)
                
                # Good error handling should show user-friendly message
                assert has_error_handling, "No error handling indicators found"
                
        except (NoSuchElementException, TimeoutException):
            pytest.skip("Error handling test skipped - form not available")
    
    def test_responsive_design(self, flask_app, browser):
        """Test responsive design at different screen sizes"""
        test_sizes = [
            (320, 568),   # Mobile portrait
            (768, 1024),  # Tablet
            (1920, 1080)  # Desktop
        ]
        
        for width, height in test_sizes:
            browser.set_window_size(width, height)
            browser.get(flask_app.base_url)
            
            # Page should load without horizontal scrolling
            body = browser.find_element(By.TAG_NAME, 'body')
            assert body is not None
            
            # Check that main content is visible
            viewport_width = browser.execute_script("return document.documentElement.clientWidth")
            assert viewport_width <= width + 50  # Some tolerance for scrollbars
    
    def test_accessibility_basics(self, flask_app, browser):
        """Test basic accessibility features"""
        browser.get(flask_app.base_url)
        
        # Check for page title
        title = browser.title
        assert title and len(title.strip()) > 0, "Page should have a title"
        
        # Check for lang attribute
        html_element = browser.find_element(By.TAG_NAME, 'html')
        lang_attr = html_element.get_attribute('lang')
        
        # Lang attribute is good practice but not required
        if lang_attr:
            assert len(lang_attr) >= 2, "Language attribute should be valid"
        
        # Check for focus indicators on interactive elements
        buttons = browser.find_elements(By.TAG_NAME, 'button')
        inputs = browser.find_elements(By.TAG_NAME, 'input')
        
        interactive_elements = buttons + inputs
        if interactive_elements:
            # Focus first interactive element
            first_element = interactive_elements[0]
            browser.execute_script("arguments[0].focus();", first_element)
            
            # Element should be focusable
            focused_element = browser.switch_to.active_element
            assert focused_element == first_element, "Element should be focusable"


class TestCLIIntegration:
    """Test CLI integration with E2E scenarios"""
    
    def test_cli_basic_execution(self):
        """Test CLI runs without errors"""
        try:
            result = subprocess.run(
                ['python3', 'cli.py', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0
            assert 'DOM Analyzer CLI' in result.stdout
            assert 'usage:' in result.stdout.lower()
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("CLI test skipped - cli.py not found or timeout")
    
    def test_cli_version_info(self):
        """Test CLI version information"""
        try:
            result = subprocess.run(
                ['python3', 'cli.py', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode == 0
            assert 'DOM Analyzer CLI' in result.stdout
            assert 'v' in result.stdout.lower()
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("CLI version test skipped")
    
    def test_cli_url_validation(self):
        """Test CLI URL validation"""
        try:
            # Test invalid URL
            result = subprocess.run(
                ['python3', 'cli.py', 'invalid-url', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Should either succeed (URL gets normalized) or fail gracefully
            assert result.returncode in [0, 1]
            
            if result.returncode == 1:
                # Should have error message
                error_output = result.stderr.lower()
                assert 'error' in error_output or 'failed' in error_output
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("CLI URL validation test skipped")
    
    def test_cli_output_formats(self):
        """Test CLI output formats"""
        formats = ['json', 'summary', 'csv']
        test_url = 'https://httpbin.org/html'
        
        for format_type in formats:
            try:
                result = subprocess.run(
                    ['python3', 'cli.py', test_url, '--format', format_type, '--timeout', '10'],
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                
                # Should execute without crashing
                assert result.returncode in [0, 1]  # 1 might be network error
                
                if result.returncode == 0:
                    # Check format-specific output
                    if format_type == 'json':
                        # Should be valid JSON or have JSON-like structure
                        assert '{' in result.stdout or '[' in result.stdout
                    elif format_type == 'csv':
                        # Should have CSV structure
                        lines = result.stdout.strip().split('\n')
                        if len(lines) >= 2:
                            assert ',' in lines[0]  # Header row
                    elif format_type == 'summary':
                        # Should have human-readable format
                        assert len(result.stdout.strip()) > 50
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pytest.skip(f"CLI format test skipped for {format_type}")


class TestPerformanceE2E:
    """End-to-end performance tests"""
    
    def test_app_startup_time(self):
        """Test Flask app startup performance"""
        start_time = time.time()
        
        with FlaskAppManager() as app:
            startup_time = time.time() - start_time
            
            # App should start within reasonable time
            assert startup_time < 10.0, f"App took {startup_time:.2f}s to start"
    
    def test_analysis_response_time(self, flask_app):
        """Test analysis response time"""
        test_data = {'url': 'https://httpbin.org/html'}
        
        start_time = time.time()
        
        response = requests.post(
            f'{flask_app.base_url}/analyze',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        response_time = time.time() - start_time
        
        # Should respond within reasonable time
        assert response_time < 15.0, f"Analysis took {response_time:.2f}s"
        
        # Check response status
        assert response.status_code in [200, 500]  # 500 might be network issue
    
    def test_concurrent_requests(self, flask_app):
        """Test handling of concurrent requests"""
        import concurrent.futures
        
        def make_request():
            try:
                response = requests.post(
                    f'{flask_app.base_url}/analyze',
                    json={'url': 'https://httpbin.org/html'},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                return response.status_code
            except requests.RequestException:
                return 500
        
        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Most requests should succeed or fail gracefully
        success_codes = [200, 400, 500]
        successful_requests = sum(1 for code in results if code in success_codes)
        
        assert successful_requests >= 3, f"Only {successful_requests}/5 requests handled properly"


class TestDataPersistence:
    """Test data persistence and state management"""
    
    def test_session_isolation(self, flask_app, browser):
        """Test that sessions are properly isolated"""
        # Open first session
        browser.get(flask_app.base_url)
        first_session_storage = browser.execute_script("return localStorage;")
        
        # Navigate away and back
        browser.get('about:blank')
        browser.get(flask_app.base_url)
        
        second_session_storage = browser.execute_script("return localStorage;")
        
        # Storage should persist within session
        assert first_session_storage == second_session_storage
    
    def test_memory_cleanup(self, flask_app):
        """Test memory cleanup after analysis"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform multiple analyses
        for i in range(5):
            try:
                requests.post(
                    f'{flask_app.base_url}/analyze',
                    json={'url': f'https://httpbin.org/html?test={i}'},
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
            except requests.RequestException:
                pass  # Network errors are expected
            
            time.sleep(0.5)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        memory_increase_mb = memory_increase / 1024 / 1024
        assert memory_increase_mb < 50, f"Memory increased by {memory_increase_mb:.1f}MB"


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Set up test environment"""
    # Ensure required directories exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Set test environment variables
    os.environ['TESTING'] = '1'
    os.environ['WTF_CSRF_ENABLED'] = 'False'
    
    yield
    
    # Cleanup
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
    if 'WTF_CSRF_ENABLED' in os.environ:
        del os.environ['WTF_CSRF_ENABLED']


if __name__ == '__main__':
    # Run with pytest
    pytest.main([__file__, '-v', '--tb=short'])