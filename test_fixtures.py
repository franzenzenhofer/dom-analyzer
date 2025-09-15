"""
Test Fixtures and Mock Data for DOM Analyzer Test Suite
Comprehensive test data covering all edge cases and scenarios
"""

import json
from typing import Dict, Any, List
from unittest.mock import Mock
import responses


class MockHTMLFixtures:
    """Mock HTML content for testing"""
    
    SIMPLE_HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Test Page</title>
        <meta name="description" content="This is a test page for DOM analysis">
    </head>
    <body>
        <h1>Welcome</h1>
        <p>This is a simple test page.</p>
    </body>
    </html>
    """
    
    COMPLEX_HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Complex Test Page - SEO Optimized</title>
        <meta name="description" content="This is a comprehensive test page with advanced features for testing DOM analysis capabilities including SEO, accessibility, and performance metrics.">
        <meta name="keywords" content="test, dom, analysis, seo, accessibility">
        <meta name="robots" content="index, follow">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="theme-color" content="#ffffff">
        
        <!-- Open Graph -->
        <meta property="og:title" content="Complex Test Page">
        <meta property="og:description" content="Testing Open Graph implementation">
        <meta property="og:image" content="https://example.com/og-image.jpg">
        <meta property="og:type" content="website">
        
        <!-- Twitter Cards -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Complex Test Page">
        <meta name="twitter:description" content="Testing Twitter Cards implementation">
        
        <!-- Security Headers -->
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
        <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
        
        <!-- Structured Data -->
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": "Complex Test Page",
            "description": "Testing structured data implementation"
        }
        </script>
        
        <!-- Styles -->
        <link rel="stylesheet" href="https://cdn.example.com/styles.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        
        <style>
        .container { max-width: 1200px; margin: 0 auto; }
        .btn-primary { background-color: #007bff; color: white; padding: 10px 20px; }
        .atomic-class { display: flex; }
        .bem-block__element--modifier { font-weight: bold; }
        </style>
        
        <!-- Canonical -->
        <link rel="canonical" href="https://example.com/test-page">
        
        <!-- Resource Hints -->
        <link rel="dns-prefetch" href="//cdn.example.com">
        <link rel="preload" href="/critical.css" as="style">
        <link rel="prefetch" href="/next-page.html">
    </head>
    <body>
        <!-- Skip Navigation -->
        <a href="#main-content" class="skip-link">Skip to main content</a>
        
        <!-- Header -->
        <header role="banner">
            <nav role="navigation" aria-label="Main navigation">
                <ul>
                    <li><a href="/" aria-current="page">Home</a></li>
                    <li><a href="/about">About</a></li>
                    <li><a href="/contact">Contact</a></li>
                </ul>
            </nav>
        </header>
        
        <!-- Main Content -->
        <main id="main-content" role="main">
            <h1>Complex Test Page</h1>
            
            <section aria-labelledby="intro-heading">
                <h2 id="intro-heading">Introduction</h2>
                <p>This is a comprehensive test page with multiple sections and advanced features.</p>
                
                <!-- Images with different scenarios -->
                <img src="/image1.jpg" alt="Test image 1" width="300" height="200" loading="lazy">
                <img src="/image2.webp" alt="Test image 2 in WebP format" width="300" height="200">
                <img src="/image3.png" alt="" role="presentation">
                <img src="/image4.jpg" width="300" height="200">  <!-- Missing alt -->
                
                <!-- Picture element -->
                <picture>
                    <source srcset="/image-large.webp" media="(min-width: 800px)" type="image/webp">
                    <source srcset="/image-large.jpg" media="(min-width: 800px)">
                    <img src="/image-small.jpg" alt="Responsive test image" loading="lazy">
                </picture>
            </section>
            
            <!-- Forms -->
            <section aria-labelledby="form-heading">
                <h2 id="form-heading">Contact Form</h2>
                <form action="/submit" method="post">
                    <fieldset>
                        <legend>Personal Information</legend>
                        
                        <label for="name">Name *</label>
                        <input type="text" id="name" name="name" required aria-describedby="name-help">
                        <small id="name-help">Enter your full name</small>
                        
                        <label for="email">Email *</label>
                        <input type="email" id="email" name="email" required autocomplete="email">
                        
                        <!-- Input without label (accessibility issue) -->
                        <input type="tel" name="phone" placeholder="Phone number">
                        
                        <label for="message">Message</label>
                        <textarea id="message" name="message" rows="4" aria-describedby="message-help"></textarea>
                        <small id="message-help">Tell us what you think</small>
                        
                        <label for="country">Country</label>
                        <select id="country" name="country">
                            <option value="">Select a country</option>
                            <option value="us">United States</option>
                            <option value="ca">Canada</option>
                            <option value="uk">United Kingdom</option>
                        </select>
                        
                        <label>
                            <input type="checkbox" name="newsletter" value="yes">
                            Subscribe to newsletter
                        </label>
                        
                        <fieldset>
                            <legend>Preferred contact method</legend>
                            <label>
                                <input type="radio" name="contact_method" value="email" checked>
                                Email
                            </label>
                            <label>
                                <input type="radio" name="contact_method" value="phone">
                                Phone
                            </label>
                        </fieldset>
                    </fieldset>
                    
                    <button type="submit">Submit Form</button>
                    <button type="reset">Reset</button>
                </form>
            </section>
            
            <!-- Lists -->
            <section>
                <h2>Lists and Tables</h2>
                
                <ul>
                    <li>Unordered list item 1</li>
                    <li>Unordered list item 2</li>
                    <li>Unordered list item 3</li>
                </ul>
                
                <ol>
                    <li>Ordered list item 1</li>
                    <li>Ordered list item 2</li>
                    <li>Ordered list item 3</li>
                </ol>
                
                <table>
                    <caption>Test Data Table</caption>
                    <thead>
                        <tr>
                            <th scope="col">Name</th>
                            <th scope="col">Age</th>
                            <th scope="col">City</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>John Doe</td>
                            <td>30</td>
                            <td>New York</td>
                        </tr>
                        <tr>
                            <td>Jane Smith</td>
                            <td>25</td>
                            <td>Los Angeles</td>
                        </tr>
                    </tbody>
                </table>
            </section>
            
            <!-- Media -->
            <section>
                <h2>Multimedia Content</h2>
                
                <video controls width="300" height="200">
                    <source src="/video.mp4" type="video/mp4">
                    <source src="/video.webm" type="video/webm">
                    <track kind="captions" src="/captions.vtt" srclang="en" label="English">
                    Your browser does not support the video tag.
                </video>
                
                <audio controls>
                    <source src="/audio.mp3" type="audio/mpeg">
                    <source src="/audio.ogg" type="audio/ogg">
                    Your browser does not support the audio element.
                </audio>
                
                <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" 
                        width="560" height="315" 
                        title="YouTube video player"
                        sandbox="allow-scripts allow-same-origin">
                </iframe>
            </section>
        </main>
        
        <!-- Aside -->
        <aside role="complementary" aria-labelledby="sidebar-heading">
            <h2 id="sidebar-heading">Related Links</h2>
            <nav aria-label="Related links">
                <ul>
                    <li><a href="/related-1" rel="related">Related Article 1</a></li>
                    <li><a href="/related-2" rel="related">Related Article 2</a></li>
                    <li><a href="https://external.com" rel="nofollow noopener" target="_blank">External Link</a></li>
                </ul>
            </nav>
        </aside>
        
        <!-- Footer -->
        <footer role="contentinfo">
            <p>&copy; 2024 Test Company. All rights reserved.</p>
            <nav aria-label="Footer navigation">
                <ul>
                    <li><a href="/privacy">Privacy Policy</a></li>
                    <li><a href="/terms">Terms of Service</a></li>
                    <li><a href="tel:+1234567890">Call Us</a></li>
                    <li><a href="sms:+1234567890">Text Us</a></li>
                </ul>
            </nav>
        </footer>
        
        <!-- Scripts -->
        <script src="https://cdn.example.com/jquery.min.js"></script>
        <script src="https://cdn.example.com/bootstrap.min.js" async></script>
        <script src="/app.js" defer></script>
        
        <script>
        // Inline script with various patterns
        const config = {
            apiUrl: '/api/v1',
            timeout: 5000
        };
        
        // Modern JavaScript patterns
        class TestClass {
            constructor(options) {
                this.options = { ...options };
            }
            
            async fetchData() {
                try {
                    const response = await fetch(config.apiUrl);
                    const data = await response.json();
                    return data;
                } catch (error) {
                    console.error('Fetch error:', error);
                }
            }
        }
        
        // Arrow functions
        const handleClick = (event) => {
            event.preventDefault();
            console.log('Button clicked');
        };
        
        // Event listeners
        document.addEventListener('DOMContentLoaded', () => {
            const buttons = document.querySelectorAll('button');
            buttons.forEach(button => {
                button.addEventListener('click', handleClick);
            });
        });
        
        // Template literals
        const message = `Welcome to the test page!`;
        
        // Service Worker registration
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }
        
        // jQuery usage
        $(document).ready(function() {
            $('.btn-primary').click(function() {
                $(this).toggleClass('active');
            });
        });
        
        // Analytics tracking
        gtag('config', 'GA_MEASUREMENT_ID');
        
        // Promise usage
        Promise.resolve()
            .then(() => console.log('Promise resolved'))
            .catch(error => console.error(error));
        </script>
        
        <!-- Tracking pixel -->
        <img src="https://analytics.example.com/pixel.gif" width="1" height="1" alt="">
        
        <!-- Social media widgets -->
        <div class="fb-like" data-href="https://example.com" data-layout="standard"></div>
        
    </body>
    </html>
    """
    
    MALFORMED_HTML = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Malformed HTML Test
        <meta name="description" content="Testing malformed HTML handling
    </head>
    <body>
        <h1>Broken HTML</h1>
        <p>This paragraph is not closed
        <div>
            <span>Nested elements without proper closing
        <img src="broken.jpg">
        <script>
        // Incomplete script
        const broken = 
    </body>
    """
    
    EMPTY_HTML = """
    <!DOCTYPE html>
    <html>
    <head><title></title></head>
    <body></body>
    </html>
    """
    
    NO_DOCTYPE_HTML = """
    <html>
    <head><title>No Doctype</title></head>
    <body><p>Missing DOCTYPE declaration</p></body>
    </html>
    """
    
    ACCESSIBILITY_ISSUES_HTML = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Accessibility Issues Test</title>
    </head>
    <body>
        <!-- Missing alt text -->
        <img src="image.jpg">
        
        <!-- Form without labels -->
        <form>
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password">
            <button type="submit">Submit</button>
        </form>
        
        <!-- Missing headings hierarchy -->
        <h3>Skipped H1 and H2</h3>
        <h5>Skipped H4</h5>
        
        <!-- Poor color contrast -->
        <p style="color: #ccc; background: white;">Low contrast text</p>
        
        <!-- Missing lang attribute -->
        <div>Some content in different language</div>
        
        <!-- No skip links -->
        <!-- Missing ARIA labels -->
        <button>Click me</button>
        
        <!-- Inaccessible table -->
        <table>
            <tr>
                <td>Header 1</td>
                <td>Header 2</td>
            </tr>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
            </tr>
        </table>
        
        <!-- Video without captions -->
        <video controls>
            <source src="video.mp4" type="video/mp4">
        </video>
    </body>
    </html>
    """
    
    SEO_ISSUES_HTML = """
    <!DOCTYPE html>
    <html>
    <head>
        <!-- Too long title -->
        <title>This is an extremely long title that exceeds the recommended character limit for SEO purposes and should be flagged as non-optimal</title>
        
        <!-- Too short meta description -->
        <meta name="description" content="Short desc">
        
        <!-- Multiple H1 tags -->
        <meta name="keywords" content="keyword stuffing, repeated keywords, keyword stuffing, repeated keywords">
    </head>
    <body>
        <h1>First H1</h1>
        <h1>Second H1</h1>
        
        <!-- Thin content -->
        <p>Very little content here.</p>
        
        <!-- No structured data -->
        <!-- No Open Graph tags -->
        <!-- No canonical URL -->
    </body>
    </html>
    """
    
    PERFORMANCE_ISSUES_HTML = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Performance Issues Test</title>
        <!-- Blocking CSS -->
        <link rel="stylesheet" href="https://external.com/large-styles.css">
        <style>
        /* Inline critical CSS would be better */
        body { margin: 0; padding: 0; }
        </style>
    </head>
    <body>
        <!-- Large images without optimization -->
        <img src="huge-image.jpg" width="100" height="100">
        <img src="another-large.png">
        
        <!-- No lazy loading -->
        <img src="below-fold1.jpg" alt="Image 1">
        <img src="below-fold2.jpg" alt="Image 2">
        <img src="below-fold3.jpg" alt="Image 3">
        
        <!-- Render-blocking scripts -->
        <script src="https://external.com/blocking-script.js"></script>
        <script>
        // Large inline script
        var largeData = [/* lots of data */];
        </script>
        
        <!-- No resource hints -->
        <!-- No compression indicators -->
        <!-- No caching headers -->
    </body>
    </html>
    """


class MockResponseFixtures:
    """Mock HTTP response data for testing"""
    
    @staticmethod
    def create_mock_response(html_content: str, status_code: int = 200, headers: Dict[str, str] = None) -> Mock:
        """Create a mock response object"""
        if headers is None:
            headers = {
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Length': str(len(html_content)),
                'Server': 'Test-Server/1.0'
            }
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.status_code = status_code
        mock_response.headers = headers
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_response.raise_for_status.return_value = None
        
        return mock_response
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get comprehensive security headers"""
        return {
            'Content-Type': 'text/html; charset=utf-8',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'Set-Cookie': 'session=abc123; Secure; HttpOnly; SameSite=Strict'
        }
    
    @staticmethod
    def get_minimal_headers() -> Dict[str, str]:
        """Get minimal headers (missing security headers)"""
        return {
            'Content-Type': 'text/html; charset=utf-8',
            'Server': 'nginx/1.18.0'
        }


class TestURLs:
    """Test URLs for different scenarios"""
    
    VALID_URLS = [
        'https://example.com',
        'https://www.example.com',
        'https://subdomain.example.com',
        'https://example.com/path/to/page',
        'https://example.com/path/to/page?query=value',
        'https://example.com:8080/secure-page',
        'http://insecure.example.com',
    ]
    
    INVALID_URLS = [
        '',
        'not-a-url',
        'ftp://example.com',
        'javascript:alert(1)',
        'https://[invalid',
        'https://.example.com',
        'https://example..com',
    ]
    
    TIMEOUT_URLS = [
        'https://httpstat.us/504?sleep=35000',  # Will timeout
        'https://never-resolving-domain-12345.com',
    ]
    
    ERROR_URLS = [
        'https://httpstat.us/404',
        'https://httpstat.us/500',
        'https://httpstat.us/503',
    ]


class ExpectedResults:
    """Expected analysis results for testing"""
    
    SIMPLE_HTML_EXPECTED = {
        'dom_complexity': {
            'total_elements': 6,  # html, head, meta, title, body, h1, p
            'max_depth': 3,  # html > body > h1/p
            'leaf_nodes': 4,  # meta, title, h1, p
            'branch_nodes': 2,  # html, head, body
        },
        'seo_signals': {
            'title': {
                'exists': True,
                'text': 'Test Page',
                'length': 9,
                'optimal': False,  # Too short
            },
            'meta_tags': {
                'description': {
                    'exists': True,
                    'length': 42,
                    'optimal': False,  # Too short
                }
            }
        },
        'accessibility': {
            'language': {
                'html_lang': 'en'
            }
        }
    }
    
    COMPLEX_HTML_EXPECTED = {
        'dom_complexity': {
            'total_elements': lambda x: x > 50,  # Many elements
            'max_depth': lambda x: x >= 5,  # Deep nesting
        },
        'seo_signals': {
            'title': {
                'exists': True,
                'optimal': True,  # Good length
            },
            'meta_tags': {
                'description': {
                    'exists': True,
                    'optimal': True,  # Good length
                }
            },
            'schema_org': {
                'json_ld_count': 1,
                'types': ['WebPage']
            },
            'open_graph': {
                'count': lambda x: x >= 4,  # Multiple OG tags
            }
        },
        'accessibility': {
            'form_labels': {
                'inputs_with_labels': lambda x: x >= 5,
                'inputs_without_labels': 1,  # Phone input missing label
            },
            'alternative_text': {
                'missing_alt': 1,  # One image without alt
                'with_alt': lambda x: x >= 3,
            }
        },
        'javascript_analysis': {
            'frameworks_detected': ['jquery'],
            'patterns': {
                'arrow_functions': lambda x: x >= 1,
                'async_await_usage': lambda x: x >= 1,
                'class_syntax': lambda x: x >= 1,
            }
        }
    }


class PerformanceBenchmarks:
    """Performance benchmark expectations"""
    
    FAST_ANALYSIS_TIME = 2.0  # seconds
    SLOW_ANALYSIS_TIME = 10.0  # seconds
    
    SMALL_PAGE_SIZE = 50000  # bytes
    LARGE_PAGE_SIZE = 1000000  # bytes
    
    SIMPLE_DOM_ELEMENTS = 50
    COMPLEX_DOM_ELEMENTS = 500
    
    ACCEPTABLE_MEMORY_USAGE = 100  # MB


class TestDataGenerator:
    """Generate test data dynamically"""
    
    @staticmethod
    def generate_large_html(num_elements: int = 1000) -> str:
        """Generate HTML with many elements for stress testing"""
        elements = []
        elements.append('<!DOCTYPE html>')
        elements.append('<html lang="en">')
        elements.append('<head><title>Large HTML Test</title></head>')
        elements.append('<body>')
        
        for i in range(num_elements):
            elements.append(f'<div id="element-{i}" class="test-class-{i % 10}">')
            elements.append(f'<p>This is paragraph {i} with some text content.</p>')
            elements.append('</div>')
        
        elements.append('</body>')
        elements.append('</html>')
        
        return '\n'.join(elements)
    
    @staticmethod
    def generate_deep_nested_html(depth: int = 20) -> str:
        """Generate deeply nested HTML for depth testing"""
        html = '<!DOCTYPE html><html><head><title>Deep Nesting Test</title></head><body>'
        
        # Create deep nesting
        for i in range(depth):
            html += f'<div class="level-{i}">'
        
        html += '<p>Deeply nested content</p>'
        
        # Close all divs
        for i in range(depth):
            html += '</div>'
        
        html += '</body></html>'
        return html
    
    @staticmethod
    def generate_many_images_html(num_images: int = 100) -> str:
        """Generate HTML with many images for image analysis testing"""
        html = '<!DOCTYPE html><html><head><title>Many Images Test</title></head><body>'
        
        formats = ['jpg', 'png', 'webp', 'gif', 'svg']
        loading_types = ['lazy', 'eager', None]
        
        for i in range(num_images):
            format_choice = formats[i % len(formats)]
            loading_choice = loading_types[i % len(loading_types)]
            
            img_attrs = [f'src="/image{i}.{format_choice}"']
            
            # Add alt text to most images
            if i % 10 != 0:  # 90% have alt text
                img_attrs.append(f'alt="Test image {i}"')
            
            # Add loading attribute to some images
            if loading_choice:
                img_attrs.append(f'loading="{loading_choice}"')
            
            # Add dimensions to some images
            if i % 3 == 0:
                img_attrs.extend(['width="300"', 'height="200"'])
            
            html += f'<img {" ".join(img_attrs)}>'
        
        html += '</body></html>'
        return html


def setup_mock_responses():
    """Setup responses mock for HTTP requests"""
    responses.add(
        responses.GET,
        'https://example.com',
        body=MockHTMLFixtures.COMPLEX_HTML,
        status=200,
        headers=MockResponseFixtures.get_security_headers()
    )
    
    responses.add(
        responses.GET,
        'https://simple.example.com',
        body=MockHTMLFixtures.SIMPLE_HTML,
        status=200,
        headers=MockResponseFixtures.get_minimal_headers()
    )
    
    responses.add(
        responses.GET,
        'https://malformed.example.com',
        body=MockHTMLFixtures.MALFORMED_HTML,
        status=200,
        headers={'Content-Type': 'text/html'}
    )
    
    responses.add(
        responses.GET,
        'https://empty.example.com',
        body=MockHTMLFixtures.EMPTY_HTML,
        status=200
    )
    
    responses.add(
        responses.GET,
        'https://httpstat.us/404',
        status=404,
        body='Not Found'
    )
    
    responses.add(
        responses.GET,
        'https://httpstat.us/500',
        status=500,
        body='Internal Server Error'
    )
    
    # Timeout simulation
    responses.add(
        responses.GET,
        'https://timeout.example.com',
        body=responses.ConnectionError('Connection timeout')
    )


class ValidationHelpers:
    """Helper functions for test validation"""
    
    @staticmethod
    def validate_dom_complexity(result: Dict[str, Any]) -> bool:
        """Validate DOM complexity results structure"""
        required_keys = ['total_elements', 'max_depth', 'leaf_nodes', 'branch_nodes', 'complexity_score']
        return all(key in result for key in required_keys)
    
    @staticmethod
    def validate_seo_signals(result: Dict[str, Any]) -> bool:
        """Validate SEO signals structure"""
        required_sections = ['title', 'meta_tags', 'headings', 'content_quality']
        return all(section in result for section in required_sections)
    
    @staticmethod
    def validate_accessibility(result: Dict[str, Any]) -> bool:
        """Validate accessibility results structure"""
        required_sections = ['aria', 'semantic_html', 'alternative_text', 'form_labels']
        return all(section in result for section in required_sections)
    
    @staticmethod
    def validate_performance_metrics(result: Dict[str, Any]) -> bool:
        """Validate performance metrics structure"""
        required_sections = ['lazy_loading', 'image_optimization', 'resource_hints']
        return all(section in result for section in required_sections)
    
    @staticmethod
    def validate_security_headers(result: Dict[str, Any]) -> bool:
        """Validate security analysis structure"""
        required_keys = ['security_score', 'headers_present']
        return all(key in result for key in required_keys)
    
    @staticmethod
    def assert_result_within_range(actual: Any, expected_range: tuple, message: str = ""):
        """Assert that a numeric result is within expected range"""
        if not isinstance(expected_range, tuple) or len(expected_range) != 2:
            raise ValueError("Expected range must be a tuple of (min, max)")
        
        min_val, max_val = expected_range
        assert min_val <= actual <= max_val, f"{message}: Expected {actual} to be between {min_val} and {max_val}"
    
    @staticmethod
    def assert_callable_expectation(actual: Any, expected_callable, message: str = ""):
        """Assert that actual value satisfies callable expectation"""
        if callable(expected_callable):
            assert expected_callable(actual), f"{message}: Expected callable failed for value {actual}"
        else:
            assert actual == expected_callable, f"{message}: Expected {expected_callable}, got {actual}"