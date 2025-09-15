"""
Core DOM Analyzer Module - Shared logic for Flask app and CLI
Extracted from analyzer_enhanced.py following DRY principles
"""

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
from typing import Dict, List, Any, Tuple, Optional
import colorsys
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
import warnings


class CoreDOMAnalyzer:
    """Core DOM Analysis Engine - Shared between Flask and CLI"""
    
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
    
    def __init__(self, url: str, timeout: int = 30, verify_ssl: bool = False):
        self.url = url
        self.parsed_url = urlparse(url)
        self.base_domain = tldextract.extract(url).registered_domain
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.responses = {}
        self.soups = {}
        self.mega_stats = defaultdict(dict)
        
    def fetch_with_all_user_agents(self) -> Dict[str, Any]:
        """Fetch the page with different user agents to detect variations"""
        results = {}
        
        # Suppress SSL warnings if verify_ssl is False
        if not self.verify_ssl:
            warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        for ua_name, ua_string in self.USER_AGENTS.items():
            headers = {'User-Agent': ua_string}
            try:
                response = requests.get(
                    self.url, 
                    headers=headers, 
                    timeout=self.timeout, 
                    verify=self.verify_ssl
                )
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
    
    def fetch_single_user_agent(self, user_agent: str = 'desktop_chrome') -> Optional[Dict[str, Any]]:
        """Fetch with a single user agent for simpler analysis"""
        if user_agent not in self.USER_AGENTS:
            user_agent = 'desktop_chrome'
            
        ua_string = self.USER_AGENTS[user_agent]
        headers = {'User-Agent': ua_string}
        
        try:
            response = requests.get(
                self.url,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            result = {
                'status_code': response.status_code,
                'content_length': len(response.text),
                'headers': dict(response.headers),
                'response_time': response.elapsed.total_seconds(),
                'html': response.text,
                'soup': BeautifulSoup(response.text, 'html.parser')
            }
            
            self.responses[user_agent] = result
            return result
            
        except Exception as e:
            error_result = {'error': str(e)}
            self.responses[user_agent] = error_result
            return None
    
    def calculate_dom_complexity(self, soup: BeautifulSoup) -> Dict[str, Any]:
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
    
    def analyze_css_selectors(self, soup: BeautifulSoup) -> Dict[str, Any]:
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
                elif '-' in cls and '__' not in cls and '--' not in cls:
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
    
    def analyze_javascript_complexity(self, soup: BeautifulSoup) -> Dict[str, Any]:
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
                        if framework not in stats['frameworks_detected']:
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
    
    def analyze_performance_metrics(self, soup: BeautifulSoup, response_data: Dict[str, Any]) -> Dict[str, Any]:
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
            if isinstance(rel, str):
                rel = [rel]
            
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
        images = soup.find_all(['img', 'source'])
        for img in images:
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
    
    def analyze_seo_signals(self, soup: BeautifulSoup) -> Dict[str, Any]:
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
        else:
            seo['title'] = {'exists': False}
        
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
        else:
            seo['meta_tags']['description'] = {'exists': False}
        
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
                if script.string:
                    data = json.loads(script.string)
                    if '@type' in data:
                        schema_types.append(data['@type'])
            except (json.JSONDecodeError, TypeError):
                pass
        seo['schema_org']['types'] = schema_types
        
        # Open Graph
        og_tags = soup.find_all('meta', property=re.compile('^og:'))
        seo['open_graph']['count'] = len(og_tags)
        seo['open_graph']['properties'] = {tag.get('property'): tag.get('content', '')[:100] for tag in og_tags[:10]}
        
        # Twitter Cards
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile('^twitter:')})
        seo['twitter_cards']['count'] = len(twitter_tags)
        twitter_card_type = soup.find('meta', attrs={'name': 'twitter:card'})
        seo['twitter_cards']['type'] = twitter_card_type.get('content') if twitter_card_type else None
        
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
        else:
            seo['robots'] = {'content': None}
        
        # Content quality
        text = soup.get_text()
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        seo['content_quality'] = {
            'word_count': len(words),
            'unique_words': len(set(words)),
            'lexical_diversity': len(set(words)) / len(words) if words else 0,
            'avg_word_length': statistics.mean([len(w) for w in words]) if words else 0,
            'sentence_count': len([s for s in sentences if s.strip()]),
            'avg_sentence_length': statistics.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0,
            'paragraph_count': len(soup.find_all('p')),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'table_count': len(soup.find_all('table')),
            'media_count': len(soup.find_all(['img', 'video', 'audio'])),
            'content_to_code_ratio': len(text) / len(str(soup)) if str(soup) else 0
        }
        
        # Keyword density (top 10 words)
        word_freq = Counter(w.lower() for w in words if len(w) > 3 and w.isalpha())
        seo['keyword_density'] = dict(word_freq.most_common(10))
        
        return seo
    
    def analyze_accessibility_advanced(self, soup: BeautifulSoup) -> Dict[str, Any]:
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
        positive_tabindex = 0
        for elem in soup.find_all(attrs={'tabindex': True}):
            try:
                if int(elem.get('tabindex', 0)) > 0:
                    positive_tabindex += 1
            except (ValueError, TypeError):
                pass
        a11y['keyboard_nav']['positive_tabindex'] = positive_tabindex
        a11y['keyboard_nav']['accesskey_elements'] = len(soup.find_all(attrs={'accesskey': True}))
        
        # Multimedia
        videos = soup.find_all('video')
        a11y['multimedia']['videos'] = len(videos)
        a11y['multimedia']['videos_with_captions'] = sum(1 for v in videos if v.find('track', kind='captions'))
        a11y['multimedia']['videos_with_transcripts'] = sum(1 for v in videos if v.find('track', kind='descriptions'))
        
        audios = soup.find_all('audio')
        a11y['multimedia']['audio_elements'] = len(audios)
        
        return a11y
    
    def analyze_security_headers(self, response_headers: Dict[str, str]) -> Dict[str, Any]:
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
        
        security['security_score'] = (actual_score / total_possible_score) * 100 if total_possible_score > 0 else 0
        
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
        else:
            security['csp'] = {'present': False}
        
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
        else:
            security['cookies'] = {'present': False}
        
        return security
    
    def count_total_statistics(self, obj: Any, count: int = 0) -> int:
        """Recursively count all statistics"""
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count = self.count_total_statistics(value, count)
        elif isinstance(obj, list):
            count += len(obj)
            for item in obj:
                count = self.count_total_statistics(item, count)
        else:
            count += 1
        return count
    
    def generate_comprehensive_analysis(self, user_agent: str = 'desktop_chrome') -> Dict[str, Any]:
        """Generate comprehensive analysis using a single user agent"""
        start_time = time.time()
        
        # Fetch page
        response_data = self.fetch_single_user_agent(user_agent)
        
        if not response_data:
            return {
                'error': f'Failed to fetch page with {user_agent}',
                'url': self.url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        soup = response_data['soup']
        
        # Run all analyses
        all_stats = {
            'url': self.url,
            'user_agent_used': user_agent,
            'fetch_info': {
                'status_code': response_data['status_code'],
                'content_length': response_data['content_length'],
                'response_time': response_data['response_time']
            },
            'dom_complexity': self.calculate_dom_complexity(soup),
            'css_analysis': self.analyze_css_selectors(soup),
            'javascript_analysis': self.analyze_javascript_complexity(soup),
            'performance_metrics': self.analyze_performance_metrics(soup, response_data),
            'seo_signals': self.analyze_seo_signals(soup),
            'accessibility': self.analyze_accessibility_advanced(soup),
            'security': self.analyze_security_headers(response_data['headers']),
        }
        
        # Calculate processing time and meta statistics
        processing_time = time.time() - start_time
        
        all_stats['meta_statistics'] = {
            'total_data_points': self.count_total_statistics(all_stats),
            'analysis_categories': len([k for k in all_stats.keys() if not k.startswith(('url', 'user_agent', 'meta_'))]),
            'processing_time': processing_time,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return all_stats


class LegacyDOMAnalyzer:
    """Legacy DOM Analyzer - Compatible with existing Flask app
    Wrapper around CoreDOMAnalyzer to maintain backward compatibility
    """
    
    def __init__(self, url: str):
        self.url = url
        self.parsed_url = urlparse(url)
        self.base_domain = tldextract.extract(url).registered_domain
        self.soup = None
        self.html_content = None
        self.core_analyzer = CoreDOMAnalyzer(url)
        self.assets = {
            'scripts': [],
            'stylesheets': [],
            'images': [],
            'fonts': [],
            'videos': [],
            'audio': [],
            'iframes': [],
            'other': []
        }
        self.domain_stats = {
            'same_origin': [],
            'subdomain': [],
            'third_party': []
        }
        self.statistics = {}
        
    def fetch_page(self) -> bool:
        """Legacy method - fetches page and sets soup"""
        response_data = self.core_analyzer.fetch_single_user_agent()
        
        if response_data:
            self.html_content = response_data['html']
            self.soup = response_data['soup']
            return True
        else:
            return False
    
    def categorize_domain(self, asset_url: str) -> Tuple[str, str]:
        """Categorize domain as same_origin, subdomain, or third_party"""
        try:
            parsed_asset = urlparse(asset_url)
            if not parsed_asset.netloc:
                asset_url = urljoin(self.url, asset_url)
                parsed_asset = urlparse(asset_url)
            
            asset_domain = tldextract.extract(asset_url)
            
            if parsed_asset.netloc == self.parsed_url.netloc:
                return 'same_origin', asset_url
            elif asset_domain.registered_domain == self.base_domain:
                return 'subdomain', asset_url
            else:
                return 'third_party', asset_url
        except Exception:
            return 'same_origin', asset_url
    
    def extract_assets(self):
        """Extract assets from the page"""
        if not self.soup:
            return
        
        # Scripts
        for script in self.soup.find_all('script'):
            src = script.get('src')
            if src:
                category, full_url = self.categorize_domain(src)
                self.assets['scripts'].append({
                    'url': full_url,
                    'category': category,
                    'type': 'external',
                    'async': script.get('async') is not None,
                    'defer': script.get('defer') is not None
                })
                self.domain_stats[category].append(full_url)
            else:
                self.assets['scripts'].append({
                    'type': 'inline',
                    'size': len(script.string) if script.string else 0
                })
        
        # Stylesheets
        for link in self.soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                category, full_url = self.categorize_domain(href)
                self.assets['stylesheets'].append({
                    'url': full_url,
                    'category': category,
                    'media': link.get('media', 'all')
                })
                self.domain_stats[category].append(full_url)
        
        # Images
        for img in self.soup.find_all(['img', 'picture', 'source']):
            src = img.get('src') or img.get('srcset') or img.get('data-src')
            if src:
                urls = re.findall(r'https?://[^\s,]+|/[^\s,]+', src)
                for url in urls:
                    category, full_url = self.categorize_domain(url)
                    self.assets['images'].append({
                        'url': full_url,
                        'category': category,
                        'alt': img.get('alt', ''),
                        'loading': img.get('loading', 'auto'),
                        'width': img.get('width'),
                        'height': img.get('height')
                    })
                    self.domain_stats[category].append(full_url)
        
        # Continue with other asset extraction as per original code...
    
    def calculate_statistics(self):
        """Calculate legacy statistics"""
        if not self.soup:
            return
        
        # Use core analyzer for advanced statistics
        comprehensive_stats = self.core_analyzer.generate_comprehensive_analysis()
        
        # Transform to legacy format
        self.statistics = {
            'html_stats': {
                'total_size': len(self.html_content) if self.html_content else 0,
                'total_tags': comprehensive_stats['dom_complexity']['total_elements'],
                'doctype': bool(self.soup.find(string=re.compile('<!DOCTYPE', re.IGNORECASE))),
                'html_lang': self.soup.html.get('lang') if self.soup.html else None,
            },
            'seo_analysis': comprehensive_stats['seo_signals'],
            'accessibility': comprehensive_stats['accessibility'],
            'performance': comprehensive_stats['performance_metrics'],
            'security': comprehensive_stats['security']
        }
    
    def analyze(self) -> Optional[Dict[str, Any]]:
        """Legacy analyze method"""
        if not self.fetch_page():
            return None
        
        self.extract_assets()
        self.calculate_statistics()
        
        return {
            'url': self.url,
            'assets': self.assets,
            'domain_stats': self.domain_stats,
            'statistics': self.statistics,
        }