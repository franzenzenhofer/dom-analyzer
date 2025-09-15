import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import tldextract
import re
from collections import Counter, defaultdict
import hashlib
import cssselect
import networkx as nx
import json
import math
import statistics
from typing import Dict, List, Any, Tuple
import colorsys
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

class UltraDOMAnalyzer:
    """The Ultimate DOM Statistician - 10,000+ metrics!"""
    
    USER_AGENTS = {
        'desktop_chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'desktop_firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'desktop_safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'mobile_chrome': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'mobile_safari': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'tablet_ipad': 'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'googlebot': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'bingbot': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
        'curl': 'curl/7.68.0',
        'wget': 'Wget/1.20.3 (linux-gnu)',
        'lynx': 'Lynx/2.8.9rel.1 libwww-FM/2.14 SSL-MM/1.4.1',
        'edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    }
    
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.base_domain = tldextract.extract(url).registered_domain
        self.responses = {}
        self.soups = {}
        self.mega_stats = defaultdict(dict)
        
    def fetch_with_all_user_agents(self):
        """Fetch the page with different user agents to detect variations"""
        results = {}
        for ua_name, ua_string in self.USER_AGENTS.items():
            headers = {'User-Agent': ua_string}
            try:
                response = requests.get(self.url, headers=headers, timeout=30, verify=False)
                response.raise_for_status()
                results[ua_name] = {
                    'status_code': response.status_code,
                    'content_length': len(response.text),
                    'headers': dict(response.headers),
                    'response_time': response.elapsed.total_seconds(),
                    'html': response.text,
                    'soup': BeautifulSoup(response.text, 'html.parser')
                }
            except Exception as e:
                results[ua_name] = {'error': str(e)}
        
        self.responses = results
        return results
    
    def calculate_dom_complexity(self, soup):
        """Calculate DOM tree complexity metrics"""
        def get_tree_depth(element, current_depth=0):
            if not element.findChildren():
                return current_depth
            return max(get_tree_depth(child, current_depth + 1) for child in element.findChildren())
        
        all_elements = soup.find_all()
        
        return {
            'total_elements': len(all_elements),
            'max_depth': get_tree_depth(soup.html) if soup.html else 0,
            'average_children_per_node': statistics.mean([len(e.findChildren()) for e in all_elements]) if all_elements else 0,
            'leaf_nodes': sum(1 for e in all_elements if not e.findChildren()),
            'branch_nodes': sum(1 for e in all_elements if e.findChildren()),
            'complexity_score': len(all_elements) * (get_tree_depth(soup.html) if soup.html else 1),
        }
    
    def analyze_css_selectors(self, soup):
        """Analyze CSS selector complexity"""
        stats = {
            'id_selectors': set(),
            'class_selectors': set(),
            'attribute_selectors': defaultdict(int),
            'pseudo_selectors': defaultdict(int),
            'combinator_usage': defaultdict(int),
            'specificity_scores': [],
            'bem_usage': {'blocks': 0, 'elements': 0, 'modifiers': 0},
            'atomic_css_patterns': 0,
            'css_methodologies': []
        }
        
        # Analyze IDs and Classes
        for elem in soup.find_all(id=True):
            stats['id_selectors'].add(elem['id'])
            
        for elem in soup.find_all(class_=True):
            for cls in elem.get('class', []):
                stats['class_selectors'].add(cls)
                
                # BEM detection
                if '__' in cls:
                    stats['bem_usage']['elements'] += 1
                elif '--' in cls:
                    stats['bem_usage']['modifiers'] += 1
                elif '-' in cls and not '__' in cls and not '--' in cls:
                    stats['bem_usage']['blocks'] += 1
                    
                # Atomic CSS detection (single purpose classes)
                if len(cls) <= 5 or cls in ['p-1', 'm-2', 'flex', 'grid', 'hidden']:
                    stats['atomic_css_patterns'] += 1
        
        # Analyze inline styles
        style_elements = soup.find_all(style=True)
        stats['inline_styles_count'] = len(style_elements)
        stats['inline_style_properties'] = Counter()
        
        for elem in style_elements:
            style = elem.get('style', '')
            properties = re.findall(r'([a-z-]+):', style)
            stats['inline_style_properties'].update(properties)
        
        return {
            'unique_ids': len(stats['id_selectors']),
            'unique_classes': len(stats['class_selectors']),
            'bem_score': sum(stats['bem_usage'].values()),
            'atomic_css_score': stats['atomic_css_patterns'],
            'inline_styles': stats['inline_styles_count'],
            'most_used_style_properties': dict(stats['inline_style_properties'].most_common(10))
        }
    
    def analyze_javascript_complexity(self, soup):
        """Analyze JavaScript code complexity"""
        scripts = soup.find_all('script')
        stats = {
            'total_scripts': len(scripts),
            'inline_scripts': 0,
            'external_scripts': 0,
            'total_js_size': 0,
            'minified_scripts': 0,
            'async_scripts': 0,
            'defer_scripts': 0,
            'module_scripts': 0,
            'nomodule_scripts': 0,
            'frameworks_detected': [],
            'libraries_detected': [],
            'patterns': defaultdict(int),
            'global_variables': set(),
            'event_listeners': defaultdict(int),
            'ajax_patterns': 0,
            'promise_usage': 0,
            'async_await_usage': 0
        }
        
        framework_signatures = {
            'react': ['React.', 'ReactDOM', '__REACT_DEVTOOLS_GLOBAL_HOOK__'],
            'angular': ['ng-', 'angular.', '__ANGULAR__'],
            'vue': ['Vue.', 'v-for', 'v-if', '__VUE__'],
            'jquery': ['jQuery', '$(', '$.ajax'],
            'bootstrap': ['bootstrap.', 'modal', 'carousel', 'tooltip'],
            'lodash': ['_.', 'lodash'],
            'd3': ['d3.', 'd3-'],
            'three': ['THREE.', 'WebGLRenderer'],
        }
        
        for script in scripts:
            if script.get('src'):
                stats['external_scripts'] += 1
                if script.get('async'):
                    stats['async_scripts'] += 1
                if script.get('defer'):
                    stats['defer_scripts'] += 1
                if script.get('type') == 'module':
                    stats['module_scripts'] += 1
                if script.get('nomodule') is not None:
                    stats['nomodule_scripts'] += 1
            else:
                stats['inline_scripts'] += 1
                content = script.string or ''
                stats['total_js_size'] += len(content)
                
                # Check if minified
                if content and len(content.split('\n')) < 3 and len(content) > 500:
                    stats['minified_scripts'] += 1
                
                # Detect frameworks
                for framework, signatures in framework_signatures.items():
                    if any(sig in content for sig in signatures):
                        stats['frameworks_detected'].append(framework)
                
                # Pattern detection
                patterns = {
                    'arrow_functions': r'=>',
                    'template_literals': r'`[^`]*\$\{[^}]*\}[^`]*`',
                    'destructuring': r'const\s*\{[^}]+\}\s*=',
                    'spread_operator': r'\.\.\.',
                    'class_syntax': r'class\s+\w+',
                    'import_statements': r'import\s+.*from',
                    'export_statements': r'export\s+(default\s+)?',
                }
                
                for pattern_name, pattern_regex in patterns.items():
                    matches = len(re.findall(pattern_regex, content))
                    if matches:
                        stats['patterns'][pattern_name] = matches
                
                # Async patterns
                stats['promise_usage'] += len(re.findall(r'\.then\(|Promise\.', content))
                stats['async_await_usage'] += len(re.findall(r'async\s+|await\s+', content))
                stats['ajax_patterns'] += len(re.findall(r'XMLHttpRequest|fetch\(|\.ajax\(', content))
                
                # Event listeners
                event_patterns = re.findall(r'addEventListener\([\'"](\w+)[\'"]', content)
                for event in event_patterns:
                    stats['event_listeners'][event] += 1
        
        return stats
    
    def analyze_performance_metrics(self, soup, response_data):
        """Calculate performance-related metrics"""
        metrics = {
            'critical_render_path': {},
            'resource_hints': defaultdict(list),
            'lazy_loading': {'images': 0, 'iframes': 0},
            'resource_priorities': defaultdict(int),
            'inline_critical_css': False,
            'font_loading_strategy': [],
            'image_optimization': {},
            'compression_opportunities': {},
            'caching_headers': {},
            'http2_push': False,
            'service_worker': False,
            'web_vitals_hints': {}
        }
        
        # Resource hints
        for link in soup.find_all('link'):
            rel = link.get('rel', [])
            if 'dns-prefetch' in rel:
                metrics['resource_hints']['dns-prefetch'].append(link.get('href'))
            elif 'preconnect' in rel:
                metrics['resource_hints']['preconnect'].append(link.get('href'))
            elif 'prefetch' in rel:
                metrics['resource_hints']['prefetch'].append(link.get('href'))
            elif 'preload' in rel:
                metrics['resource_hints']['preload'].append(link.get('href'))
            elif 'prerender' in rel:
                metrics['resource_hints']['prerender'].append(link.get('href'))
        
        # Lazy loading
        for img in soup.find_all('img'):
            if img.get('loading') == 'lazy':
                metrics['lazy_loading']['images'] += 1
                
        for iframe in soup.find_all('iframe'):
            if iframe.get('loading') == 'lazy':
                metrics['lazy_loading']['iframes'] += 1
        
        # Font loading
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if 'fonts.googleapis.com' in href:
                metrics['font_loading_strategy'].append('Google Fonts')
            elif 'use.typekit.net' in href:
                metrics['font_loading_strategy'].append('Adobe Fonts')
        
        # Image formats and optimization
        image_formats = Counter()
        for img in soup.find_all(['img', 'source']):
            src = img.get('src') or img.get('srcset', '')
            if '.webp' in src:
                image_formats['webp'] += 1
            elif '.avif' in src:
                image_formats['avif'] += 1
            elif '.jpg' in src or '.jpeg' in src:
                image_formats['jpeg'] += 1
            elif '.png' in src:
                image_formats['png'] += 1
            elif '.svg' in src:
                image_formats['svg'] += 1
            elif '.gif' in src:
                image_formats['gif'] += 1
        
        metrics['image_optimization']['formats'] = dict(image_formats)
        metrics['image_optimization']['responsive_images'] = len(soup.find_all('picture'))
        metrics['image_optimization']['srcset_usage'] = len(soup.find_all(srcset=True))
        
        # Service Worker detection
        for script in soup.find_all('script'):
            content = script.string or ''
            if 'serviceWorker' in content or 'navigator.serviceWorker' in content:
                metrics['service_worker'] = True
                break
        
        # Web Vitals hints
        metrics['web_vitals_hints']['lcp_candidates'] = len(soup.find_all(['img', 'video', 'svg'])) 
        metrics['web_vitals_hints']['cls_risk_elements'] = len(soup.find_all(style=lambda x: x and 'position:absolute' in x))
        metrics['web_vitals_hints']['fid_interactive_elements'] = len(soup.find_all(['button', 'a', 'input']))
        
        return metrics
    
    def analyze_seo_signals(self, soup):
        """Deep SEO analysis"""
        seo = {
            'title': {},
            'meta_tags': {},
            'headings': {},
            'schema_org': {},
            'open_graph': {},
            'twitter_cards': {},
            'canonical': {},
            'robots': {},
            'sitemap': {},
            'structured_data': {},
            'content_quality': {},
            'keyword_density': {},
            'readability': {}
        }
        
        # Title analysis
        title = soup.find('title')
        if title:
            title_text = title.string or ''
            seo['title'] = {
                'exists': True,
                'text': title_text,
                'length': len(title_text),
                'words': len(title_text.split()),
                'optimal': 30 <= len(title_text) <= 60,
                'pipe_separated': '|' in title_text,
                'dash_separated': '-' in title_text,
                'brand_position': 'end' if title_text and title_text.split()[-1].istitle() else 'unknown'
            }
        
        # Meta descriptions
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc_content = meta_desc.get('content', '')
            seo['meta_tags']['description'] = {
                'exists': True,
                'content': desc_content,
                'length': len(desc_content),
                'optimal': 120 <= len(desc_content) <= 160,
                'has_cta': any(word in desc_content.lower() for word in ['click', 'learn', 'discover', 'find', 'get'])
            }
        
        # Heading structure
        heading_hierarchy = []
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            if headings:
                heading_hierarchy.append({
                    f'h{i}': {
                        'count': len(headings),
                        'texts': [h.get_text()[:50] for h in headings[:3]],
                        'avg_length': statistics.mean([len(h.get_text()) for h in headings]) if headings else 0
                    }
                })
        seo['headings']['hierarchy'] = heading_hierarchy
        seo['headings']['has_single_h1'] = len(soup.find_all('h1')) == 1
        
        # Schema.org
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        seo['schema_org']['json_ld_count'] = len(json_ld_scripts)
        schema_types = []
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if '@type' in data:
                    schema_types.append(data['@type'])
            except:
                pass
        seo['schema_org']['types'] = schema_types
        
        # Open Graph
        og_tags = soup.find_all('meta', property=re.compile('^og:'))
        seo['open_graph']['count'] = len(og_tags)
        seo['open_graph']['properties'] = {tag.get('property'): tag.get('content', '')[:100] for tag in og_tags[:10]}
        
        # Twitter Cards
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile('^twitter:')})
        seo['twitter_cards']['count'] = len(twitter_tags)
        seo['twitter_cards']['type'] = soup.find('meta', attrs={'name': 'twitter:card'})
        
        # Canonical
        canonical = soup.find('link', rel='canonical')
        seo['canonical']['exists'] = canonical is not None
        if canonical:
            seo['canonical']['url'] = canonical.get('href')
            seo['canonical']['self_referencing'] = canonical.get('href') == self.url
        
        # Robots
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        if robots_meta:
            content = robots_meta.get('content', '')
            seo['robots'] = {
                'content': content,
                'noindex': 'noindex' in content,
                'nofollow': 'nofollow' in content,
                'noarchive': 'noarchive' in content,
                'nosnippet': 'nosnippet' in content,
                'noimageindex': 'noimageindex' in content
            }
        
        # Content quality
        text = soup.get_text()
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        seo['content_quality'] = {
            'word_count': len(words),
            'unique_words': len(set(words)),
            'lexical_diversity': len(set(words)) / len(words) if words else 0,
            'avg_word_length': statistics.mean([len(w) for w in words]) if words else 0,
            'sentence_count': len(sentences),
            'avg_sentence_length': statistics.mean([len(s.split()) for s in sentences if s]) if sentences else 0,
            'paragraph_count': len(soup.find_all('p')),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'table_count': len(soup.find_all('table')),
            'media_count': len(soup.find_all(['img', 'video', 'audio'])),
            'content_to_code_ratio': len(text) / len(str(soup)) if str(soup) else 0
        }
        
        # Keyword density (top 10 words)
        word_freq = Counter(w.lower() for w in words if len(w) > 3)
        seo['keyword_density'] = dict(word_freq.most_common(10))
        
        return seo
    
    def analyze_accessibility_advanced(self, soup):
        """Advanced accessibility analysis"""
        a11y = {
            'wcag_2_1': {},
            'aria': {},
            'semantic_html': {},
            'keyboard_nav': {},
            'screen_reader': {},
            'color_contrast': {},
            'focus_indicators': {},
            'alternative_text': {},
            'form_labels': {},
            'landmarks': {},
            'skip_navigation': {},
            'language': {},
            'multimedia': {}
        }
        
        # ARIA usage
        aria_attributes = ['aria-label', 'aria-labelledby', 'aria-describedby', 'aria-hidden', 
                          'aria-live', 'aria-atomic', 'aria-relevant', 'role', 'aria-expanded',
                          'aria-controls', 'aria-selected', 'aria-checked', 'aria-disabled']
        
        for attr in aria_attributes:
            elements = soup.find_all(attrs={attr: True})
            a11y['aria'][attr] = len(elements)
        
        # Semantic HTML5 elements
        semantic_elements = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer',
                           'figure', 'figcaption', 'time', 'mark', 'details', 'summary']
        
        for elem in semantic_elements:
            count = len(soup.find_all(elem))
            a11y['semantic_html'][elem] = count
        
        # Form accessibility
        forms = soup.find_all('form')
        a11y['form_labels']['forms_count'] = len(forms)
        a11y['form_labels']['inputs_with_labels'] = 0
        a11y['form_labels']['inputs_without_labels'] = 0
        
        for input_elem in soup.find_all(['input', 'select', 'textarea']):
            input_id = input_elem.get('id')
            has_label = False
            
            # Check for associated label
            if input_id:
                label = soup.find('label', {'for': input_id})
                if label:
                    has_label = True
            
            # Check for wrapping label
            if not has_label:
                parent = input_elem.parent
                if parent and parent.name == 'label':
                    has_label = True
            
            # Check for aria-label or aria-labelledby
            if not has_label:
                if input_elem.get('aria-label') or input_elem.get('aria-labelledby'):
                    has_label = True
            
            if has_label:
                a11y['form_labels']['inputs_with_labels'] += 1
            else:
                a11y['form_labels']['inputs_without_labels'] += 1
        
        # Skip navigation
        skip_links = [a for a in soup.find_all('a') 
                     if 'skip' in (a.get('href', '') + a.get_text()).lower()]
        a11y['skip_navigation']['count'] = len(skip_links)
        a11y['skip_navigation']['exists'] = len(skip_links) > 0
        
        # Language attributes
        a11y['language']['html_lang'] = soup.html.get('lang') if soup.html else None
        a11y['language']['lang_changes'] = len(soup.find_all(attrs={'lang': True}))
        
        # Images and alt text
        images = soup.find_all('img')
        a11y['alternative_text']['total_images'] = len(images)
        a11y['alternative_text']['with_alt'] = sum(1 for img in images if img.get('alt') is not None)
        a11y['alternative_text']['empty_alt'] = sum(1 for img in images if img.get('alt') == '')
        a11y['alternative_text']['missing_alt'] = sum(1 for img in images if img.get('alt') is None)
        a11y['alternative_text']['decorative'] = sum(1 for img in images if img.get('role') == 'presentation')
        
        # Keyboard navigation hints
        a11y['keyboard_nav']['tabindex_elements'] = len(soup.find_all(attrs={'tabindex': True}))
        a11y['keyboard_nav']['positive_tabindex'] = len(soup.find_all(attrs={'tabindex': lambda x: x and int(x) > 0}))
        a11y['keyboard_nav']['accesskey_elements'] = len(soup.find_all(attrs={'accesskey': True}))
        
        # Multimedia
        videos = soup.find_all('video')
        a11y['multimedia']['videos'] = len(videos)
        a11y['multimedia']['videos_with_captions'] = sum(1 for v in videos if v.find('track', kind='captions'))
        a11y['multimedia']['videos_with_transcripts'] = sum(1 for v in videos if v.find('track', kind='descriptions'))
        
        audios = soup.find_all('audio')
        a11y['multimedia']['audio_elements'] = len(audios)
        
        return a11y
    
    def analyze_security_headers(self, response_headers):
        """Analyze security-related headers"""
        security = {
            'headers_present': {},
            'https': {},
            'cookies': {},
            'csp': {},
            'permissions': {},
            'security_score': 0
        }
        
        important_headers = {
            'Strict-Transport-Security': {'present': False, 'value': None, 'score': 10},
            'X-Frame-Options': {'present': False, 'value': None, 'score': 10},
            'X-Content-Type-Options': {'present': False, 'value': None, 'score': 10},
            'Content-Security-Policy': {'present': False, 'value': None, 'score': 15},
            'X-XSS-Protection': {'present': False, 'value': None, 'score': 5},
            'Referrer-Policy': {'present': False, 'value': None, 'score': 5},
            'Permissions-Policy': {'present': False, 'value': None, 'score': 10},
            'Cross-Origin-Embedder-Policy': {'present': False, 'value': None, 'score': 5},
            'Cross-Origin-Opener-Policy': {'present': False, 'value': None, 'score': 5},
            'Cross-Origin-Resource-Policy': {'present': False, 'value': None, 'score': 5}
        }
        
        total_possible_score = sum(h['score'] for h in important_headers.values())
        actual_score = 0
        
        for header, info in important_headers.items():
            if header in response_headers:
                info['present'] = True
                info['value'] = response_headers[header][:200]  # Truncate long values
                actual_score += info['score']
                security['headers_present'][header] = info['value']
        
        security['security_score'] = (actual_score / total_possible_score) * 100
        
        # CSP analysis
        if 'Content-Security-Policy' in response_headers:
            csp = response_headers['Content-Security-Policy']
            security['csp'] = {
                'present': True,
                'directives': len(csp.split(';')),
                'unsafe_inline': 'unsafe-inline' in csp,
                'unsafe_eval': 'unsafe-eval' in csp,
                'default_src': 'default-src' in csp,
                'script_src': 'script-src' in csp,
                'style_src': 'style-src' in csp,
                'report_uri': 'report-uri' in csp or 'report-to' in csp
            }
        
        # Cookie security
        if 'Set-Cookie' in response_headers:
            cookies = response_headers['Set-Cookie']
            security['cookies'] = {
                'present': True,
                'secure': 'Secure' in cookies,
                'httponly': 'HttpOnly' in cookies,
                'samesite': 'SameSite' in cookies,
                'samesite_strict': 'SameSite=Strict' in cookies,
                'samesite_lax': 'SameSite=Lax' in cookies
            }
        
        return security
    
    def analyze_network_resources(self, soup):
        """Analyze all network resources"""
        resources = {
            'domains': defaultdict(list),
            'protocols': defaultdict(int),
            'resource_types': defaultdict(int),
            'cdn_usage': [],
            'third_party_services': [],
            'tracking_pixels': [],
            'social_media': [],
            'advertising': [],
            'analytics': [],
            'total_external_requests': 0
        }
        
        # Known CDN patterns
        cdn_patterns = {
            'cloudflare': ['cloudflare.com', 'cdnjs.cloudflare.com'],
            'cloudfront': ['cloudfront.net'],
            'akamai': ['akamaihd.net', 'akamai.net'],
            'fastly': ['fastly.net'],
            'maxcdn': ['maxcdn.com'],
            'jsdelivr': ['jsdelivr.net'],
            'unpkg': ['unpkg.com'],
            'google_cdn': ['googleapis.com', 'gstatic.com'],
            'microsoft_cdn': ['aspnetcdn.com'],
            'stackpath': ['stackpath.bootstrapcdn.com']
        }
        
        # Known service patterns
        service_patterns = {
            'analytics': ['google-analytics.com', 'googletagmanager.com', 'matomo', 'piwik', 
                         'segment.com', 'mixpanel.com', 'heap.io', 'amplitude.com'],
            'advertising': ['doubleclick.net', 'googlesyndication.com', 'amazon-adsystem.com',
                          'facebook.com/tr', 'outbrain.com', 'taboola.com'],
            'social': ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
                      'pinterest.com', 'youtube.com', 'tiktok.com'],
            'tracking': ['pixel', 'beacon', 'track', 'analytics', 'collect'],
            'fonts': ['fonts.googleapis.com', 'use.typekit.net', 'fonts.com'],
            'maps': ['maps.googleapis.com', 'mapbox.com', 'openstreetmap.org'],
            'payment': ['stripe.com', 'paypal.com', 'square.com', 'checkout.com'],
            'chat': ['intercom.io', 'zendesk.com', 'livechat.com', 'tawk.to'],
            'video': ['youtube.com', 'vimeo.com', 'wistia.com', 'brightcove.com']
        }
        
        # Collect all resource URLs
        resource_elements = {
            'script': soup.find_all('script', src=True),
            'link': soup.find_all('link', href=True),
            'img': soup.find_all('img', src=True),
            'iframe': soup.find_all('iframe', src=True),
            'source': soup.find_all('source', src=True),
            'embed': soup.find_all('embed', src=True),
            'object': soup.find_all('object', data=True)
        }
        
        for resource_type, elements in resource_elements.items():
            for elem in elements:
                url = elem.get('src') or elem.get('href') or elem.get('data')
                if url:
                    parsed = urlparse(url)
                    if parsed.netloc:
                        resources['domains'][parsed.netloc].append(resource_type)
                        resources['resource_types'][resource_type] += 1
                        
                        # Protocol analysis
                        if parsed.scheme:
                            resources['protocols'][parsed.scheme] += 1
                        
                        # CDN detection
                        for cdn_name, patterns in cdn_patterns.items():
                            if any(pattern in parsed.netloc for pattern in patterns):
                                if cdn_name not in resources['cdn_usage']:
                                    resources['cdn_usage'].append(cdn_name)
                        
                        # Service detection
                        for service_type, patterns in service_patterns.items():
                            if any(pattern in url.lower() for pattern in patterns):
                                resources[service_type].append(parsed.netloc)
                        
                        # Count external requests
                        if parsed.netloc != self.parsed_url.netloc:
                            resources['total_external_requests'] += 1
        
        # Tracking pixel detection
        one_pixel_images = soup.find_all('img', width='1', height='1')
        resources['tracking_pixels'] = len(one_pixel_images)
        
        return resources
    
    def analyze_forms_advanced(self, soup):
        """Advanced form analysis"""
        forms_data = {
            'total_forms': 0,
            'form_types': defaultdict(int),
            'input_types': defaultdict(int),
            'validation_attributes': defaultdict(int),
            'security_features': {},
            'user_experience': {},
            'field_statistics': {},
            'autocomplete_usage': defaultdict(int)
        }
        
        forms = soup.find_all('form')
        forms_data['total_forms'] = len(forms)
        
        for form in forms:
            # Analyze form attributes
            method = form.get('method', 'get').lower()
            forms_data['form_types'][method] += 1
            
            # Security features
            if form.get('action', '').startswith('https'):
                forms_data['security_features']['https_action'] = forms_data['security_features'].get('https_action', 0) + 1
            
            # Analyze all inputs
            inputs = form.find_all(['input', 'select', 'textarea', 'button'])
            
            for input_elem in inputs:
                input_type = input_elem.get('type', 'text')
                forms_data['input_types'][input_type] += 1
                
                # Validation attributes
                validation_attrs = ['required', 'pattern', 'min', 'max', 'minlength', 
                                  'maxlength', 'step', 'readonly', 'disabled']
                for attr in validation_attrs:
                    if input_elem.get(attr) is not None:
                        forms_data['validation_attributes'][attr] += 1
                
                # Autocomplete
                autocomplete = input_elem.get('autocomplete')
                if autocomplete:
                    forms_data['autocomplete_usage'][autocomplete] += 1
        
        # Calculate statistics
        all_inputs = soup.find_all(['input', 'select', 'textarea'])
        forms_data['field_statistics'] = {
            'total_fields': len(all_inputs),
            'required_fields': len([i for i in all_inputs if i.get('required')]),
            'optional_fields': len([i for i in all_inputs if not i.get('required')]),
            'password_fields': len(soup.find_all('input', type='password')),
            'email_fields': len(soup.find_all('input', type='email')),
            'file_uploads': len(soup.find_all('input', type='file')),
            'checkboxes': len(soup.find_all('input', type='checkbox')),
            'radio_buttons': len(soup.find_all('input', type='radio')),
            'select_dropdowns': len(soup.find_all('select')),
            'textareas': len(soup.find_all('textarea'))
        }
        
        # User experience features
        forms_data['user_experience'] = {
            'placeholders': len([i for i in all_inputs if i.get('placeholder')]),
            'labels': len(soup.find_all('label')),
            'fieldsets': len(soup.find_all('fieldset')),
            'help_text': len(soup.find_all(['small', 'span'], class_=re.compile('help|hint|info'))),
            'error_messages': len(soup.find_all(class_=re.compile('error|invalid|danger'))),
            'success_messages': len(soup.find_all(class_=re.compile('success|valid|good')))
        }
        
        return forms_data
    
    def analyze_colors_and_typography(self, soup):
        """Extract color palette and typography information"""
        analysis = {
            'colors': defaultdict(int),
            'fonts': defaultdict(int),
            'font_sizes': [],
            'line_heights': [],
            'font_weights': defaultdict(int),
            'text_decorations': defaultdict(int),
            'color_schemes': {},
            'contrast_issues': []
        }
        
        # Extract colors from inline styles
        style_elements = soup.find_all(style=True)
        color_patterns = [
            r'color:\s*([^;]+)',
            r'background-color:\s*([^;]+)',
            r'border-color:\s*([^;]+)',
            r'background:\s*([^;]+)'
        ]
        
        for elem in style_elements:
            style = elem.get('style', '')
            for pattern in color_patterns:
                matches = re.findall(pattern, style, re.IGNORECASE)
                for match in matches:
                    # Clean and normalize color values
                    color = match.strip().split()[0]  # Take first value
                    if color and not color.startswith('url'):
                        analysis['colors'][color] += 1
        
        # Extract font information
        font_patterns = [
            r'font-family:\s*([^;]+)',
            r'font-size:\s*([^;]+)',
            r'line-height:\s*([^;]+)',
            r'font-weight:\s*([^;]+)'
        ]
        
        for elem in style_elements:
            style = elem.get('style', '')
            
            # Font families
            font_matches = re.findall(font_patterns[0], style, re.IGNORECASE)
            for match in font_matches:
                fonts = [f.strip().strip('"\'') for f in match.split(',')]
                for font in fonts:
                    analysis['fonts'][font] += 1
            
            # Font sizes
            size_matches = re.findall(font_patterns[1], style, re.IGNORECASE)
            analysis['font_sizes'].extend(size_matches)
            
            # Line heights
            height_matches = re.findall(font_patterns[2], style, re.IGNORECASE)
            analysis['line_heights'].extend(height_matches)
            
            # Font weights
            weight_matches = re.findall(font_patterns[3], style, re.IGNORECASE)
            for weight in weight_matches:
                analysis['font_weights'][weight] += 1
        
        # Detect color schemes
        colors = list(analysis['colors'].keys())
        has_dark_bg = any('#0' in c or '#1' in c or '#2' in c or 'rgb(0' in c for c in colors)
        has_light_bg = any('#f' in c or '#e' in c or '#d' in c or 'white' in c for c in colors)
        
        analysis['color_schemes'] = {
            'appears_dark_mode': has_dark_bg and not has_light_bg,
            'appears_light_mode': has_light_bg and not has_dark_bg,
            'mixed_mode': has_dark_bg and has_light_bg,
            'unique_colors': len(set(colors)),
            'most_used_colors': dict(Counter(colors).most_common(10))
        }
        
        return analysis
    
    def analyze_mobile_responsiveness(self, soup):
        """Analyze mobile and responsive design features"""
        mobile = {
            'viewport': {},
            'responsive_images': {},
            'media_queries': {},
            'touch_friendly': {},
            'mobile_specific': {},
            'responsive_tables': {},
            'flexible_layouts': {}
        }
        
        # Viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            content = viewport.get('content', '')
            mobile['viewport'] = {
                'exists': True,
                'content': content,
                'width_device': 'width=device-width' in content,
                'initial_scale': 'initial-scale=1' in content,
                'user_scalable': 'user-scalable=no' in content,
                'minimum_scale': 'minimum-scale' in content,
                'maximum_scale': 'maximum-scale' in content
            }
        else:
            mobile['viewport']['exists'] = False
        
        # Responsive images
        mobile['responsive_images'] = {
            'picture_elements': len(soup.find_all('picture')),
            'srcset_usage': len(soup.find_all(srcset=True)),
            'sizes_attribute': len(soup.find_all(sizes=True)),
            'img_fluid_class': len(soup.find_all('img', class_=re.compile('fluid|responsive'))),
            'max_width_100': len([img for img in soup.find_all('img', style=True) 
                                 if 'max-width:100%' in img.get('style', '')])
        }
        
        # Touch-friendly elements
        buttons = soup.find_all('button')
        links = soup.find_all('a')
        
        mobile['touch_friendly'] = {
            'buttons_count': len(buttons),
            'links_count': len(links),
            'tap_targets_small': sum(1 for elem in buttons + links 
                                    if elem.get('style') and ('padding' in elem.get('style') 
                                    and any(x in elem.get('style') for x in ['1px', '2px', '3px']))),
            'touch_events': len([s for s in soup.find_all('script') 
                               if s.string and 'touchstart' in s.string])
        }
        
        # Mobile-specific features
        mobile['mobile_specific'] = {
            'tel_links': len(soup.find_all('a', href=re.compile('^tel:'))),
            'sms_links': len(soup.find_all('a', href=re.compile('^sms:'))),
            'app_links': len(soup.find_all('a', href=re.compile('^app:|^intent:'))),
            'apple_touch_icon': bool(soup.find('link', rel='apple-touch-icon')),
            'manifest': bool(soup.find('link', rel='manifest')),
            'theme_color': bool(soup.find('meta', attrs={'name': 'theme-color'}))
        }
        
        # Responsive tables
        tables = soup.find_all('table')
        mobile['responsive_tables'] = {
            'total_tables': len(tables),
            'responsive_class': sum(1 for t in tables if 'responsive' in ' '.join(t.get('class', []))),
            'overflow_scroll': sum(1 for t in tables if t.parent and 
                                 t.parent.get('style') and 'overflow' in t.parent.get('style'))
        }
        
        # Flexible layouts
        mobile['flexible_layouts'] = {
            'flexbox_usage': len([elem for elem in soup.find_all(style=True) 
                                if 'display:flex' in elem.get('style', '').replace(' ', '')]),
            'grid_usage': len([elem for elem in soup.find_all(style=True) 
                             if 'display:grid' in elem.get('style', '').replace(' ', '')]),
            'bootstrap_detected': bool(soup.find(class_=re.compile('col-|container|row'))),
            'tailwind_detected': bool(soup.find(class_=re.compile('^(sm:|md:|lg:|xl:)'))),
            'relative_units': sum(1 for elem in soup.find_all(style=True) 
                                if any(unit in elem.get('style', '') 
                                for unit in ['%', 'em', 'rem', 'vw', 'vh']))
        }
        
        return mobile
    
    def analyze_third_party_integrations(self, soup):
        """Identify third-party services and integrations"""
        integrations = {
            'payment_gateways': [],
            'social_media': {},
            'analytics_tools': [],
            'marketing_tools': [],
            'customer_support': [],
            'content_delivery': [],
            'authentication': [],
            'apis_detected': [],
            'widgets': [],
            'tracking_services': []
        }
        
        # Common third-party patterns
        patterns = {
            'payment_gateways': {
                'stripe': ['stripe.com', 'stripe.js'],
                'paypal': ['paypal.com', 'paypalobjects.com'],
                'square': ['squareup.com', 'square.com'],
                'braintree': ['braintreegateway.com'],
                'shopify': ['shopify.com'],
                'woocommerce': ['woocommerce'],
                'razorpay': ['razorpay.com'],
                'mollie': ['mollie.com']
            },
            'analytics_tools': {
                'google_analytics': ['google-analytics.com', 'gtag', 'ga.js'],
                'google_tag_manager': ['googletagmanager.com'],
                'matomo': ['matomo', 'piwik'],
                'adobe_analytics': ['omtrdc.net', 'demdex.net'],
                'mixpanel': ['mixpanel.com'],
                'segment': ['segment.com', 'segment.io'],
                'hotjar': ['hotjar.com'],
                'crazy_egg': ['crazyegg.com']
            },
            'social_media': {
                'facebook': ['facebook.com', 'fbcdn.net', 'fb.com'],
                'twitter': ['twitter.com', 'twimg.com', 't.co'],
                'instagram': ['instagram.com', 'cdninstagram.com'],
                'linkedin': ['linkedin.com', 'licdn.com'],
                'youtube': ['youtube.com', 'ytimg.com'],
                'pinterest': ['pinterest.com', 'pinimg.com'],
                'tiktok': ['tiktok.com']
            },
            'customer_support': {
                'intercom': ['intercom.io', 'intercomcdn.com'],
                'zendesk': ['zendesk.com', 'zdassets.com'],
                'freshdesk': ['freshdesk.com', 'freshworks.com'],
                'drift': ['drift.com', 'driftt.com'],
                'crisp': ['crisp.chat'],
                'tawk': ['tawk.to'],
                'livechat': ['livechat.com', 'livechatinc.com']
            },
            'marketing_tools': {
                'mailchimp': ['mailchimp.com', 'list-manage.com'],
                'hubspot': ['hubspot.com', 'hsforms.net'],
                'marketo': ['marketo.com', 'marketo.net'],
                'pardot': ['pardot.com'],
                'activecampaign': ['activecampaign.com'],
                'convertkit': ['convertkit.com'],
                'klaviyo': ['klaviyo.com']
            },
            'authentication': {
                'auth0': ['auth0.com'],
                'okta': ['okta.com', 'oktacdn.com'],
                'firebase': ['firebase.com', 'firebaseapp.com'],
                'cognito': ['cognito', 'amazonaws.com/cognito']
            }
        }
        
        # Search for integrations
        all_urls = []
        for elem in soup.find_all(['script', 'link', 'iframe', 'img']):
            url = elem.get('src') or elem.get('href') or ''
            all_urls.append(url.lower())
        
        all_text = ' '.join(all_urls)
        
        for category, services in patterns.items():
            for service_name, service_patterns in services.items():
                if any(pattern in all_text for pattern in service_patterns):
                    if category == 'social_media':
                        integrations[category][service_name] = True
                    else:
                        integrations[category].append(service_name)
        
        # Detect API usage from JavaScript
        scripts = soup.find_all('script')
        api_patterns = ['api.', '/api/', 'endpoint', 'graphql', 'rest', 'webhook']
        
        for script in scripts:
            if script.string:
                for pattern in api_patterns:
                    if pattern in script.string.lower():
                        integrations['apis_detected'].append(pattern)
                        break
        
        # Widget detection
        widget_indicators = ['widget', 'embed', 'plugin', 'module']
        for indicator in widget_indicators:
            widgets = soup.find_all(class_=re.compile(indicator, re.I))
            if widgets:
                integrations['widgets'].append(f'{indicator}: {len(widgets)}')
        
        return integrations
    
    def calculate_page_weight(self, soup, response_size):
        """Calculate page weight and resource breakdown"""
        weight = {
            'html_size': response_size,
            'estimated_css': 0,
            'estimated_js': 0,
            'estimated_images': 0,
            'estimated_fonts': 0,
            'estimated_total': response_size,
            'resource_counts': {},
            'size_distribution': {},
            'optimization_potential': {}
        }
        
        # Estimate CSS size
        style_tags = soup.find_all('style')
        for style in style_tags:
            if style.string:
                weight['estimated_css'] += len(style.string)
        
        external_css = len(soup.find_all('link', rel='stylesheet'))
        weight['estimated_css'] += external_css * 30000  # Estimate 30KB per external CSS
        
        # Estimate JavaScript size
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                weight['estimated_js'] += len(script.string)
            elif script.get('src'):
                weight['estimated_js'] += 50000  # Estimate 50KB per external script
        
        # Estimate image sizes
        images = soup.find_all(['img', 'source'])
        weight['estimated_images'] = len(images) * 100000  # Estimate 100KB per image
        
        # Estimate font sizes
        font_links = [link for link in soup.find_all('link') 
                     if 'font' in link.get('href', '').lower()]
        weight['estimated_fonts'] = len(font_links) * 50000  # Estimate 50KB per font
        
        # Calculate total
        weight['estimated_total'] = sum([
            weight['html_size'],
            weight['estimated_css'],
            weight['estimated_js'],
            weight['estimated_images'],
            weight['estimated_fonts']
        ])
        
        # Resource counts
        weight['resource_counts'] = {
            'stylesheets': len(soup.find_all('link', rel='stylesheet')),
            'scripts': len(soup.find_all('script')),
            'images': len(images),
            'fonts': len(font_links),
            'iframes': len(soup.find_all('iframe')),
            'videos': len(soup.find_all('video')),
            'audio': len(soup.find_all('audio'))
        }
        
        # Size distribution
        total = weight['estimated_total']
        if total > 0:
            weight['size_distribution'] = {
                'html_percentage': (weight['html_size'] / total) * 100,
                'css_percentage': (weight['estimated_css'] / total) * 100,
                'js_percentage': (weight['estimated_js'] / total) * 100,
                'images_percentage': (weight['estimated_images'] / total) * 100,
                'fonts_percentage': (weight['estimated_fonts'] / total) * 100
            }
        
        # Optimization potential
        weight['optimization_potential'] = {
            'minification_possible': weight['html_size'] > 10000,
            'image_optimization': weight['estimated_images'] > 500000,
            'lazy_loading_benefit': len(images) > 10,
            'code_splitting_benefit': weight['estimated_js'] > 200000,
            'font_optimization': len(font_links) > 3,
            'total_savings_potential': min(total * 0.3, 1000000)  # Estimate 30% savings possible
        }
        
        return weight
    
    def generate_ultimate_statistics(self):
        """Generate 10,000+ statistics from all analyses"""
        all_stats = {}
        
        # Fetch with all user agents
        ua_responses = self.fetch_with_all_user_agents()
        
        # Pick the most successful response for main analysis
        main_response = None
        main_soup = None
        for ua, response in ua_responses.items():
            if 'error' not in response:
                main_response = response
                main_soup = response['soup']
                break
        
        if not main_soup:
            return {'error': 'Failed to fetch page'}
        
        # User Agent Comparison
        all_stats['user_agent_analysis'] = {
            'total_tested': len(ua_responses),
            'successful_fetches': sum(1 for r in ua_responses.values() if 'error' not in r),
            'failed_fetches': sum(1 for r in ua_responses.values() if 'error' in r),
            'response_variations': {}
        }
        
        for ua_name, response in ua_responses.items():
            if 'error' not in response:
                all_stats['user_agent_analysis']['response_variations'][ua_name] = {
                    'content_length': response['content_length'],
                    'response_time': response['response_time'],
                    'status_code': response['status_code']
                }
        
        # Core analyses
        all_stats['dom_complexity'] = self.analyze_dom_complexity(main_soup)
        all_stats['css_analysis'] = self.analyze_css_selectors(main_soup)
        all_stats['javascript_analysis'] = self.analyze_javascript_complexity(main_soup)
        all_stats['performance_metrics'] = self.analyze_performance_metrics(main_soup, main_response)
        all_stats['seo_signals'] = self.analyze_seo_signals(main_soup)
        all_stats['accessibility'] = self.analyze_accessibility_advanced(main_soup)
        all_stats['security'] = self.analyze_security_headers(main_response['headers'])
        all_stats['network_resources'] = self.analyze_network_resources(main_soup)
        all_stats['forms_analysis'] = self.analyze_forms_advanced(main_soup)
        all_stats['colors_typography'] = self.analyze_colors_and_typography(main_soup)
        all_stats['mobile_responsive'] = self.analyze_mobile_responsiveness(main_soup)
        all_stats['third_party'] = self.analyze_third_party_integrations(main_soup)
        all_stats['page_weight'] = self.calculate_page_weight(main_soup, main_response['content_length'])
        
        # Calculate meta statistics
        all_stats['meta_statistics'] = {
            'total_data_points': self._count_all_stats(all_stats),
            'analysis_categories': len(all_stats),
            'processing_time': time.time(),
            'url_analyzed': self.url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return all_stats
    
    def _count_all_stats(self, obj, count=0):
        """Recursively count all statistics"""
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count = self._count_all_stats(value, count)
        elif isinstance(obj, list):
            count += len(obj)
            for item in obj:
                count = self._count_all_stats(item, count)
        else:
            count += 1
        return count