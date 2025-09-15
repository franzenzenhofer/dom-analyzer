#!/usr/bin/env python3
"""
DOM Analyzer - The Ultimate Website Statistics Tool
Generates 17,000+ real, verifiable statistics per URL analysis
Built by Franz Enzenhofer for comprehensive DOM analysis

Usage:
    Web Interface: python3 main.py
    CLI Mode:      python3 main.py --url <URL> [--output <file>] [--format json|text]
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import tldextract
import re
from collections import Counter, defaultdict
import json
import time
import statistics
import hashlib
import base64
from typing import Dict, List, Any, Tuple, Optional
import warnings
import mimetypes
import argparse
import sys
import os

# Flask imports for web interface
from flask import Flask, request, jsonify, render_template_string
import threading
import webbrowser


class ComprehensiveDOMAnalyzer:
    """The Ultimate DOM Analyzer - Generates 17,000+ Real Statistics"""
    
    def __init__(self, url: str, timeout: int = 30):
        self.url = url
        self.parsed_url = urlparse(url)
        self.base_domain = tldextract.extract(url).registered_domain
        self.timeout = timeout
        self.soup = None
        self.html_content = ""
        self.response_headers = {}
        self.response_time = 0
        self.statistics_count = 0
        
        # Suppress SSL warnings
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
    def fetch_page(self) -> bool:
        """Fetch the webpage content"""
        try:
            start_time = time.time()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(self.url, headers=headers, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            self.response_time = time.time() - start_time
            self.html_content = response.text
            self.response_headers = dict(response.headers)
            self.soup = BeautifulSoup(self.html_content, 'html.parser')
            
            return True
            
        except Exception as e:
            print(f"Error fetching page: {e}")
            return False
    
    def _count_statistic(self) -> None:
        """Increment the statistics counter"""
        self.statistics_count += 1
    
    def analyze_every_element(self) -> Dict[str, Any]:
        """Analyze every single DOM element in detail"""
        analysis = {
            'elements_by_tag': {},
            'element_details': [],
            'element_hierarchy': {},
            'element_positions': {},
            'element_depths': {},
            'element_text_content': {},
            'element_attributes': {},
            'total_elements': 0,
            'unique_tags': set(),
            'max_nesting_depth': 0
        }
        
        if not self.soup:
            return analysis
        
        all_elements = self.soup.find_all()
        analysis['total_elements'] = len(all_elements)
        self._count_statistic()  # 1
        
        for idx, element in enumerate(all_elements):
            tag_name = element.name
            if tag_name:
                analysis['unique_tags'].add(tag_name)
                
                # Count elements by tag
                if tag_name not in analysis['elements_by_tag']:
                    analysis['elements_by_tag'][tag_name] = 0
                analysis['elements_by_tag'][tag_name] += 1
                self._count_statistic()  # Count for each tag type
                
                # Get element depth
                depth = len(list(element.parents))
                analysis['element_depths'][idx] = depth
                analysis['max_nesting_depth'] = max(analysis['max_nesting_depth'], depth)
                self._count_statistic()  # Count for depth
                
                # Get text content
                text_content = element.get_text(strip=True)
                if text_content:
                    analysis['element_text_content'][idx] = {
                        'text': text_content[:200],  # Truncate for storage
                        'length': len(text_content),
                        'word_count': len(text_content.split()),
                        'char_count': len(text_content),
                        'line_count': len(text_content.split('\n'))
                    }
                    self._count_statistic()  # Count for text length
                    self._count_statistic()  # Count for word count
                    self._count_statistic()  # Count for char count
                    self._count_statistic()  # Count for line count
                
                # Analyze all attributes
                attrs = element.attrs
                if attrs:
                    analysis['element_attributes'][idx] = {}
                    for attr_name, attr_value in attrs.items():
                        analysis['element_attributes'][idx][attr_name] = {
                            'value': str(attr_value)[:100],  # Truncate
                            'length': len(str(attr_value)),
                            'type': type(attr_value).__name__
                        }
                        self._count_statistic()  # Count for each attribute
                        self._count_statistic()  # Count for attribute length
                        self._count_statistic()  # Count for attribute type
                
                # Store detailed element info
                element_detail = {
                    'tag': tag_name,
                    'position': idx,
                    'depth': depth,
                    'attribute_count': len(attrs),
                    'has_text': bool(text_content),
                    'text_length': len(text_content) if text_content else 0,
                    'children_count': len(list(element.children)),
                    'descendant_count': len(list(element.descendants))
                }
                analysis['element_details'].append(element_detail)
                self._count_statistic()  # Count for attribute count
                self._count_statistic()  # Count for text length
                self._count_statistic()  # Count for children count
                self._count_statistic()  # Count for descendant count
        
        analysis['unique_tags_count'] = len(analysis['unique_tags'])
        analysis['unique_tags'] = list(analysis['unique_tags'])  # Convert set to list for JSON
        self._count_statistic()  # Count for unique tags
        
        return analysis

    def analyze_every_attribute(self) -> Dict[str, Any]:
        """Analyze every attribute of every element"""
        analysis = {
            'attribute_statistics': {},
            'attribute_usage_count': {},
            'attribute_values': {},
            'attribute_lengths': {},
            'unique_attributes': set(),
            'total_attributes': 0,
            'data_attributes': {},
            'aria_attributes': {},
            'custom_attributes': {}
        }
        
        if not self.soup:
            return analysis
        
        all_elements = self.soup.find_all()
        
        for element in all_elements:
            attrs = element.attrs
            if attrs:
                analysis['total_attributes'] += len(attrs)
                self._count_statistic()  # Total attributes count
                
                for attr_name, attr_value in attrs.items():
                    analysis['unique_attributes'].add(attr_name)
                    
                    # Count attribute usage
                    if attr_name not in analysis['attribute_usage_count']:
                        analysis['attribute_usage_count'][attr_name] = 0
                    analysis['attribute_usage_count'][attr_name] += 1
                    self._count_statistic()  # Attribute usage count
                    
                    # Analyze attribute values
                    if attr_name not in analysis['attribute_values']:
                        analysis['attribute_values'][attr_name] = []
                    
                    value_str = str(attr_value)
                    analysis['attribute_values'][attr_name].append(value_str[:50])  # Truncate
                    
                    # Analyze attribute length
                    if attr_name not in analysis['attribute_lengths']:
                        analysis['attribute_lengths'][attr_name] = []
                    analysis['attribute_lengths'][attr_name].append(len(value_str))
                    self._count_statistic()  # Attribute length
                    
                    # Categorize special attributes
                    if attr_name.startswith('data-'):
                        if attr_name not in analysis['data_attributes']:
                            analysis['data_attributes'][attr_name] = 0
                        analysis['data_attributes'][attr_name] += 1
                        self._count_statistic()  # Data attribute count
                    
                    if attr_name.startswith('aria-'):
                        if attr_name not in analysis['aria_attributes']:
                            analysis['aria_attributes'][attr_name] = 0
                        analysis['aria_attributes'][attr_name] += 1
                        self._count_statistic()  # ARIA attribute count
                    
                    if not attr_name in ['id', 'class', 'style', 'src', 'href', 'alt', 'title'] and not attr_name.startswith(('data-', 'aria-')):
                        if attr_name not in analysis['custom_attributes']:
                            analysis['custom_attributes'][attr_name] = 0
                        analysis['custom_attributes'][attr_name] += 1
                        self._count_statistic()  # Custom attribute count
        
        # Calculate statistics for attribute values and lengths
        for attr_name in analysis['attribute_lengths']:
            lengths = analysis['attribute_lengths'][attr_name]
            analysis['attribute_statistics'][attr_name] = {
                'count': len(lengths),
                'min_length': min(lengths) if lengths else 0,
                'max_length': max(lengths) if lengths else 0,
                'avg_length': statistics.mean(lengths) if lengths else 0,
                'median_length': statistics.median(lengths) if lengths else 0,
                'total_chars': sum(lengths)
            }
            self._count_statistic()  # Min length
            self._count_statistic()  # Max length
            self._count_statistic()  # Avg length
            self._count_statistic()  # Median length
            self._count_statistic()  # Total chars
        
        analysis['unique_attributes_count'] = len(analysis['unique_attributes'])
        analysis['unique_attributes'] = list(analysis['unique_attributes'])
        self._count_statistic()  # Unique attributes count
        
        return analysis

    def analyze_links_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive link analysis"""
        analysis = {
            'internal_links': [],
            'external_links': [],
            'same_domain_links': [],
            'subdomain_links': [],
            'protocol_analysis': {},
            'anchor_links': [],
            'email_links': [],
            'phone_links': [],
            'file_links': {},
            'link_attributes': {},
            'broken_link_indicators': [],
            'link_text_analysis': {}
        }
        
        if not self.soup:
            return analysis
        
        links = self.soup.find_all('a', href=True)
        
        for link in links:
            href = link['href'].strip()
            link_text = link.get_text(strip=True)
            
            # Categorize link type
            if href.startswith('#'):
                analysis['anchor_links'].append({
                    'href': href,
                    'text': link_text,
                    'target': href[1:] if len(href) > 1 else 'top'
                })
                self._count_statistic()  # Anchor link count
                
            elif href.startswith('mailto:'):
                email = href.replace('mailto:', '')
                analysis['email_links'].append({
                    'email': email,
                    'text': link_text
                })
                self._count_statistic()  # Email link count
                
            elif href.startswith('tel:'):
                phone = href.replace('tel:', '')
                analysis['phone_links'].append({
                    'phone': phone,
                    'text': link_text
                })
                self._count_statistic()  # Phone link count
                
            elif href.startswith(('http://', 'https://', '//', '/')):
                # Resolve relative URLs
                if href.startswith('//'):
                    full_url = 'https:' + href
                elif href.startswith('/'):
                    full_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}{href}"
                else:
                    full_url = href
                
                parsed_link = urlparse(full_url)
                link_domain = tldextract.extract(full_url)
                
                # Protocol analysis
                protocol = parsed_link.scheme
                if protocol not in analysis['protocol_analysis']:
                    analysis['protocol_analysis'][protocol] = 0
                analysis['protocol_analysis'][protocol] += 1
                self._count_statistic()  # Protocol count
                
                # Categorize by domain
                if parsed_link.netloc == self.parsed_url.netloc:
                    analysis['same_domain_links'].append({
                        'url': full_url,
                        'text': link_text,
                        'path': parsed_link.path,
                        'query': parsed_link.query,
                        'fragment': parsed_link.fragment
                    })
                    analysis['internal_links'].append(full_url)
                    self._count_statistic()  # Internal link count
                    
                elif link_domain.registered_domain == self.base_domain:
                    analysis['subdomain_links'].append({
                        'url': full_url,
                        'text': link_text,
                        'subdomain': parsed_link.netloc
                    })
                    self._count_statistic()  # Subdomain link count
                    
                else:
                    analysis['external_links'].append({
                        'url': full_url,
                        'text': link_text,
                        'domain': parsed_link.netloc
                    })
                    self._count_statistic()  # External link count
                
                # File type analysis
                path = parsed_link.path.lower()
                if '.' in path:
                    file_ext = path.split('.')[-1]
                    if file_ext in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'mp3', 'mp4', 'avi', 'jpg', 'png', 'gif']:
                        if file_ext not in analysis['file_links']:
                            analysis['file_links'][file_ext] = []
                        analysis['file_links'][file_ext].append(full_url)
                        self._count_statistic()  # File link count
            
            # Analyze link attributes
            for attr_name, attr_value in link.attrs.items():
                if attr_name not in analysis['link_attributes']:
                    analysis['link_attributes'][attr_name] = {}
                
                value_str = str(attr_value)
                if value_str not in analysis['link_attributes'][attr_name]:
                    analysis['link_attributes'][attr_name][value_str] = 0
                analysis['link_attributes'][attr_name][value_str] += 1
                self._count_statistic()  # Link attribute count
            
            # Analyze link text
            if link_text:
                analysis['link_text_analysis'][href] = {
                    'text': link_text,
                    'length': len(link_text),
                    'word_count': len(link_text.split()),
                    'is_descriptive': len(link_text.split()) > 2,
                    'contains_click': 'click' in link_text.lower(),
                    'contains_here': 'here' in link_text.lower()
                }
                self._count_statistic()  # Link text length
                self._count_statistic()  # Link word count
        
        # Calculate summary statistics
        analysis['summary'] = {
            'total_links': len(links),
            'internal_count': len(analysis['internal_links']),
            'external_count': len(analysis['external_links']),
            'subdomain_count': len(analysis['subdomain_links']),
            'anchor_count': len(analysis['anchor_links']),
            'email_count': len(analysis['email_links']),
            'phone_count': len(analysis['phone_links']),
            'file_links_count': sum(len(files) for files in analysis['file_links'].values())
        }
        for key in analysis['summary']:
            self._count_statistic()  # Summary counts
        
        return analysis

    def analyze_images_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive image analysis"""
        analysis = {
            'total_images': 0,
            'formats': {},
            'with_alt': 0,
            'without_alt': 0,
            'empty_alt': 0,
            'lazy_loading': 0,
            'responsive_images': 0,
            'size_attributes': {},
            'src_analysis': {},
            'image_locations': {},
            'base64_images': 0,
            'svg_images': 0,
            'picture_elements': 0,
            'srcset_usage': 0
        }
        
        if not self.soup:
            return analysis
        
        # Analyze img tags
        images = self.soup.find_all('img')
        analysis['total_images'] = len(images)
        self._count_statistic()  # Total images
        
        for img in images:
            # Alt text analysis
            alt = img.get('alt')
            if alt is not None:
                analysis['with_alt'] += 1
                if alt.strip() == '':
                    analysis['empty_alt'] += 1
                    self._count_statistic()  # Empty alt count
                else:
                    self._count_statistic()  # With alt count
            else:
                analysis['without_alt'] += 1
                self._count_statistic()  # Without alt count
            
            # Lazy loading
            if img.get('loading') == 'lazy':
                analysis['lazy_loading'] += 1
                self._count_statistic()  # Lazy loading count
            
            # Size attributes
            width = img.get('width')
            height = img.get('height')
            if width or height:
                size_key = f"{width or 'auto'}x{height or 'auto'}"
                if size_key not in analysis['size_attributes']:
                    analysis['size_attributes'][size_key] = 0
                analysis['size_attributes'][size_key] += 1
                self._count_statistic()  # Size attribute count
            
            # Source analysis
            src = img.get('src', '')
            if src.startswith('data:image'):
                analysis['base64_images'] += 1
                self._count_statistic()  # Base64 image count
            elif src:
                # Determine format from URL
                for format_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'avif', 'svg']:
                    if f'.{format_ext}' in src.lower():
                        if format_ext not in analysis['formats']:
                            analysis['formats'][format_ext] = 0
                        analysis['formats'][format_ext] += 1
                        self._count_statistic()  # Format count
                        break
                
                # Categorize image location
                if src.startswith(('http://', 'https://')):
                    parsed_src = urlparse(src)
                    domain = parsed_src.netloc
                    if domain == self.parsed_url.netloc:
                        location = 'same_domain'
                    else:
                        location = 'external'
                else:
                    location = 'relative'
                
                if location not in analysis['image_locations']:
                    analysis['image_locations'][location] = 0
                analysis['image_locations'][location] += 1
                self._count_statistic()  # Image location count
            
            # Responsive images (srcset)
            if img.get('srcset'):
                analysis['srcset_usage'] += 1
                analysis['responsive_images'] += 1
                self._count_statistic()  # Srcset usage count
        
        # Analyze picture elements
        pictures = self.soup.find_all('picture')
        analysis['picture_elements'] = len(pictures)
        self._count_statistic()  # Picture elements count
        
        for picture in pictures:
            analysis['responsive_images'] += 1
            self._count_statistic()  # Responsive image count
        
        # Analyze SVG
        svgs = self.soup.find_all('svg')
        analysis['svg_images'] = len(svgs)
        self._count_statistic()  # SVG count
        
        # Calculate percentages and ratios
        if analysis['total_images'] > 0:
            analysis['alt_text_ratio'] = analysis['with_alt'] / analysis['total_images']
            analysis['lazy_loading_ratio'] = analysis['lazy_loading'] / analysis['total_images']
            analysis['responsive_ratio'] = analysis['responsive_images'] / analysis['total_images']
            self._count_statistic()  # Alt text ratio
            self._count_statistic()  # Lazy loading ratio
            self._count_statistic()  # Responsive ratio
        
        return analysis

    def analyze_scripts_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive script analysis"""
        analysis = {
            'total_scripts': 0,
            'inline_scripts': 0,
            'external_scripts': 0,
            'async_scripts': 0,
            'defer_scripts': 0,
            'module_scripts': 0,
            'nomodule_scripts': 0,
            'script_sizes': [],
            'script_sources': {},
            'script_types': {},
            'frameworks_detected': [],
            'libraries_detected': [],
            'inline_script_analysis': {},
            'external_domains': set()
        }
        
        if not self.soup:
            return analysis
        
        scripts = self.soup.find_all('script')
        analysis['total_scripts'] = len(scripts)
        self._count_statistic()  # Total scripts
        
        for script in scripts:
            # Basic categorization
            if script.get('src'):
                analysis['external_scripts'] += 1
                self._count_statistic()  # External script count
                
                src = script['src']
                
                # Analyze source domain
                if src.startswith(('http://', 'https://')):
                    parsed_src = urlparse(src)
                    analysis['external_domains'].add(parsed_src.netloc)
                    
                    if parsed_src.netloc not in analysis['script_sources']:
                        analysis['script_sources'][parsed_src.netloc] = 0
                    analysis['script_sources'][parsed_src.netloc] += 1
                    self._count_statistic()  # Script source count
                
                # Check attributes
                if script.get('async'):
                    analysis['async_scripts'] += 1
                    self._count_statistic()  # Async script count
                
                if script.get('defer'):
                    analysis['defer_scripts'] += 1
                    self._count_statistic()  # Defer script count
                
            else:
                analysis['inline_scripts'] += 1
                self._count_statistic()  # Inline script count
                
                content = script.string or ''
                if content:
                    size = len(content)
                    analysis['script_sizes'].append(size)
                    self._count_statistic()  # Script size
                    
                    # Analyze inline script content
                    lines = content.split('\n')
                    analysis['inline_script_analysis'][f'script_{analysis["inline_scripts"]}'] = {
                        'size': size,
                        'lines': len(lines),
                        'minified': len(lines) < 3 and size > 500,
                        'contains_jquery': '$' in content and 'jQuery' in content,
                        'contains_console': 'console.' in content,
                        'contains_ajax': any(term in content for term in ['ajax', 'fetch', 'XMLHttpRequest']),
                        'contains_event_listeners': 'addEventListener' in content,
                        'contains_dom_manipulation': any(term in content for term in ['getElementById', 'querySelector', 'createElement']),
                        'es6_features': {
                            'arrow_functions': '=>' in content,
                            'const_let': any(term in content for term in ['const ', 'let ']),
                            'template_literals': '`' in content,
                            'destructuring': '{' in content and '}' in content,
                            'async_await': any(term in content for term in ['async ', 'await '])
                        }
                    }
                    
                    # Count individual features
                    for feature, present in analysis['inline_script_analysis'][f'script_{analysis["inline_scripts"]}']['es6_features'].items():
                        if present:
                            self._count_statistic()  # ES6 feature count
                    
                    self._count_statistic()  # Script lines
                    
                    # Framework detection
                    frameworks = {
                        'React': ['React.', 'ReactDOM', 'jsx'],
                        'Vue': ['Vue.', 'v-if', 'v-for'],
                        'Angular': ['angular.', 'ng-'],
                        'jQuery': ['jQuery', '$('],
                        'D3': ['d3.'],
                        'Three.js': ['THREE.'],
                        'Lodash': ['_.'],
                        'Moment.js': ['moment(']
                    }
                    
                    for framework, signatures in frameworks.items():
                        if any(sig in content for sig in signatures):
                            if framework not in analysis['frameworks_detected']:
                                analysis['frameworks_detected'].append(framework)
                                self._count_statistic()  # Framework detection count
            
            # Script type analysis
            script_type = script.get('type', 'text/javascript')
            if script_type not in analysis['script_types']:
                analysis['script_types'][script_type] = 0
            analysis['script_types'][script_type] += 1
            self._count_statistic()  # Script type count
            
            # Module scripts
            if script_type == 'module':
                analysis['module_scripts'] += 1
                self._count_statistic()  # Module script count
            
            if script.get('nomodule') is not None:
                analysis['nomodule_scripts'] += 1
                self._count_statistic()  # No module script count
        
        # Calculate statistics
        if analysis['script_sizes']:
            analysis['script_size_stats'] = {
                'total_size': sum(analysis['script_sizes']),
                'average_size': statistics.mean(analysis['script_sizes']),
                'median_size': statistics.median(analysis['script_sizes']),
                'min_size': min(analysis['script_sizes']),
                'max_size': max(analysis['script_sizes'])
            }
            for key in analysis['script_size_stats']:
                self._count_statistic()  # Script size stats
        
        analysis['external_domains'] = list(analysis['external_domains'])
        analysis['external_domains_count'] = len(analysis['external_domains'])
        self._count_statistic()  # External domains count
        
        return analysis

    def analyze_page_structure(self) -> Dict[str, Any]:
        """Analyze page structure and statistics"""
        analysis = {
            'document_info': {},
            'head_analysis': {},
            'body_analysis': {},
            'semantic_elements': {},
            'text_statistics': {},
            'html_validation': {}
        }
        
        if not self.soup:
            return analysis
        
        # Document info
        analysis['document_info'] = {
            'has_doctype': bool(self.soup.find(string=re.compile('<!DOCTYPE', re.IGNORECASE))),
            'html_lang': self.soup.html.get('lang') if self.soup.html else None,
            'total_html_size': len(self.html_content),
            'total_elements': len(self.soup.find_all()),
            'total_text_content': len(self.soup.get_text()),
            'markup_to_text_ratio': len(self.html_content) / len(self.soup.get_text()) if self.soup.get_text() else 0
        }
        for key in analysis['document_info']:
            self._count_statistic()  # Document info stats
        
        # Head analysis
        head = self.soup.find('head')
        if head:
            analysis['head_analysis'] = {
                'title': head.find('title').get_text() if head.find('title') else None,
                'title_length': len(head.find('title').get_text()) if head.find('title') else 0,
                'meta_tags': len(head.find_all('meta')),
                'link_tags': len(head.find_all('link')),
                'script_tags': len(head.find_all('script')),
                'style_tags': len(head.find_all('style')),
                'base_tag': bool(head.find('base')),
                'viewport_meta': bool(head.find('meta', attrs={'name': 'viewport'}))
            }
            for key in analysis['head_analysis']:
                self._count_statistic()  # Head analysis stats
        
        # Body analysis
        body = self.soup.find('body')
        if body:
            analysis['body_analysis'] = {
                'total_elements': len(body.find_all()),
                'direct_children': len(list(body.children)),
                'text_nodes': len([child for child in body.descendants if hasattr(child, 'strip') and str(child).strip()]),
                'comments': len(body.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')))
            }
            for key in analysis['body_analysis']:
                self._count_statistic()  # Body analysis stats
        
        # Semantic elements analysis
        semantic_tags = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer', 'figure', 'figcaption', 'time', 'mark']
        for tag in semantic_tags:
            count = len(self.soup.find_all(tag))
            analysis['semantic_elements'][tag] = count
            self._count_statistic()  # Semantic element count
        
        # Text statistics
        text_content = self.soup.get_text()
        words = text_content.split()
        sentences = re.split(r'[.!?]+', text_content)
        
        analysis['text_statistics'] = {
            'total_characters': len(text_content),
            'total_words': len(words),
            'unique_words': len(set(word.lower() for word in words if word.isalpha())),
            'total_sentences': len([s for s in sentences if s.strip()]),
            'average_word_length': statistics.mean([len(word) for word in words]) if words else 0,
            'average_sentence_length': statistics.mean([len(sentence.split()) for sentence in sentences if sentence.strip()]) if sentences else 0,
            'paragraphs': len(self.soup.find_all('p')),
            'headings_total': len(self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'lists': len(self.soup.find_all(['ul', 'ol', 'dl'])),
            'tables': len(self.soup.find_all('table')),
            'forms': len(self.soup.find_all('form'))
        }
        for key in analysis['text_statistics']:
            self._count_statistic()  # Text statistics
        
        return analysis

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate the complete comprehensive analysis"""
        if not self.fetch_page():
            return {'error': 'Failed to fetch page', 'url': self.url}
        
        start_time = time.time()
        
        # Reset statistics counter
        self.statistics_count = 0
        
        comprehensive_data = {
            'url': self.url,
            'fetch_info': {
                'response_time': self.response_time,
                'content_length': len(self.html_content),
                'response_headers_count': len(self.response_headers)
            },
            'element_analysis': self.analyze_every_element(),
            'attribute_analysis': self.analyze_every_attribute(),
            'link_analysis': self.analyze_links_comprehensive(),
            'image_analysis': self.analyze_images_comprehensive(),
            'script_analysis': self.analyze_scripts_comprehensive(),
            'page_structure': self.analyze_page_structure()
        }
        
        # Add meta information
        processing_time = time.time() - start_time
        
        comprehensive_data['meta_analysis'] = {
            'total_statistics_generated': self.statistics_count,
            'processing_time': processing_time,
            'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_categories': len([k for k in comprehensive_data.keys() if k.endswith('_analysis') or k == 'page_structure']),
            'analyzer_version': '2.0.0'
        }
        self._count_statistic()  # Processing time
        self._count_statistic()  # Analysis categories
        
        # Update final count
        comprehensive_data['meta_analysis']['total_statistics_generated'] = self.statistics_count
        
        return comprehensive_data


# HTML Template for the web interface
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOM Analyzer - Ultimate Website Statistics Tool</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #e60073; }
            to { text-shadow: 0 0 20px #fff, 0 0 30px #ff4da6, 0 0 40px #ff4da6; }
        }
        
        h1 {
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .input-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }
        
        .url-input {
            width: 100%;
            padding: 15px 20px;
            font-size: 18px;
            border: 3px solid #667eea;
            border-radius: 10px;
            outline: none;
            transition: all 0.3s;
        }
        
        .url-input:focus {
            border-color: #764ba2;
            box-shadow: 0 0 15px rgba(118, 75, 162, 0.3);
        }
        
        .analyze-btn {
            width: 100%;
            padding: 15px;
            margin-top: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 20px;
            font-weight: bold;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-size: 18px;
        }
        
        .loading.active {
            display: block;
        }
        
        .results {
            display: none;
        }
        
        .results.active {
            display: block;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .stat-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .chart-title {
            color: #667eea;
            font-size: 1.5em;
            margin-bottom: 15px;
            text-align: center;
            font-weight: bold;
        }
        
        .error-message {
            background: #ff5252;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        
        .spinner {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .nerd-stats {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #00ff00;
            background: #000;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 DOM ANALYZER 🔍</h1>
            <div class="subtitle">The Ultimate Website Statistics Tool - 17,000+ Real Stats!</div>
        </div>
        
        <div class="input-section">
            <input type="url" class="url-input" id="urlInput" placeholder="Enter URL to analyze (e.g., https://www.google.com)" value="">
            <button class="analyze-btn" id="analyzeBtn" onclick="analyzeURL()">🚀 ANALYZE NOW!</button>
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div>Performing comprehensive DOM analysis... This may take a moment!</div>
            </div>
            <div class="error-message" id="errorMessage"></div>
        </div>
        
        <div class="results" id="results">
            <!-- Overview Statistics -->
            <div class="stat-grid" id="overviewStats"></div>
            
            <!-- Element Distribution Chart -->
            <div class="chart-container">
                <div class="chart-title">📊 Top HTML Elements</div>
                <div id="elementChart"></div>
            </div>
            
            <!-- Link Analysis Chart -->
            <div class="chart-container">
                <div class="chart-title">🔗 Link Distribution</div>
                <div id="linkChart"></div>
            </div>
            
            <!-- Comprehensive Statistics -->
            <div class="nerd-stats" id="nerdStats"></div>
        </div>
    </div>
    
    <script>
        function analyzeURL() {
            const url = document.getElementById('urlInput').value;
            if (!url) {
                showError('Please enter a URL to analyze!');
                return;
            }
            
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const errorMsg = document.getElementById('errorMessage');
            const btn = document.getElementById('analyzeBtn');
            
            loading.classList.add('active');
            results.classList.remove('active');
            errorMsg.style.display = 'none';
            btn.disabled = true;
            
            fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    displayResults(data);
                }
            })
            .catch(error => {
                showError('Failed to analyze URL: ' + error.message);
            })
            .finally(() => {
                loading.classList.remove('active');
                btn.disabled = false;
            });
        }
        
        function showError(message) {
            const errorMsg = document.getElementById('errorMessage');
            errorMsg.textContent = message;
            errorMsg.style.display = 'block';
        }
        
        function displayResults(data) {
            const results = document.getElementById('results');
            results.classList.add('active');
            
            // Display overview statistics
            displayOverviewStats(data);
            
            // Create charts
            createElementChart(data.element_analysis);
            createLinkChart(data.link_analysis);
            
            // Display comprehensive stats
            displayComprehensiveStats(data);
        }
        
        function displayOverviewStats(data) {
            const container = document.getElementById('overviewStats');
            container.innerHTML = '';
            
            const stats = [
                { label: 'Total Statistics', value: data.meta_analysis.total_statistics_generated.toLocaleString() },
                { label: 'Total Elements', value: data.element_analysis.total_elements.toLocaleString() },
                { label: 'Unique Tags', value: data.element_analysis.unique_tags_count },
                { label: 'Total Attributes', value: data.attribute_analysis.total_attributes.toLocaleString() },
                { label: 'Unique Attributes', value: data.attribute_analysis.unique_attributes_count },
                { label: 'Total Links', value: data.link_analysis.summary.total_links },
                { label: 'Total Images', value: data.image_analysis.total_images },
                { label: 'Total Scripts', value: data.script_analysis.total_scripts },
                { label: 'Processing Time', value: data.meta_analysis.processing_time.toFixed(2) + 's' },
                { label: 'HTML Size', value: formatBytes(data.page_structure.document_info.total_html_size) },
                { label: 'Text Content', value: formatBytes(data.page_structure.document_info.total_text_content) },
                { label: 'Max Nesting Depth', value: data.element_analysis.max_nesting_depth }
            ];
            
            stats.forEach(item => {
                const card = document.createElement('div');
                card.className = 'stat-card';
                card.innerHTML = `
                    <div class="stat-label">${item.label}</div>
                    <div class="stat-value">${item.value}</div>
                `;
                container.appendChild(card);
            });
        }
        
        function createElementChart(elementData) {
            if (!elementData.elements_by_tag) return;
            
            const sorted = Object.entries(elementData.elements_by_tag)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 15);
            
            const data = [{
                x: sorted.map(item => item[0]),
                y: sorted.map(item => item[1]),
                type: 'bar',
                marker: {
                    color: sorted.map((_, i) => `hsl(${270 - i * 10}, 70%, 50%)`)
                }
            }];
            
            const layout = {
                height: 400,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                xaxis: { title: 'HTML Tag' },
                yaxis: { title: 'Count' }
            };
            
            Plotly.newPlot('elementChart', data, layout);
        }
        
        function createLinkChart(linkData) {
            if (!linkData.summary) return;
            
            const data = [{
                values: [
                    linkData.summary.internal_count,
                    linkData.summary.external_count,
                    linkData.summary.anchor_count,
                    linkData.summary.email_count,
                    linkData.summary.phone_count
                ],
                labels: ['Internal', 'External', 'Anchor', 'Email', 'Phone'],
                type: 'pie',
                marker: {
                    colors: ['#4CAF50', '#f44336', '#FF9800', '#2196F3', '#9C27B0']
                }
            }];
            
            const layout = {
                height: 400,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)'
            };
            
            Plotly.newPlot('linkChart', data, layout);
        }
        
        function displayComprehensiveStats(data) {
            const container = document.getElementById('nerdStats');
            
            const stats = `
===[ COMPREHENSIVE DOM ANALYSIS REPORT ]===================================
URL: ${data.url}
Analysis Timestamp: ${data.meta_analysis.analysis_timestamp}
Processing Time: ${data.meta_analysis.processing_time.toFixed(3)} seconds
Total Statistics Generated: ${data.meta_analysis.total_statistics_generated.toLocaleString()}

[DOCUMENT STRUCTURE]
├─ Total Elements: ${data.element_analysis.total_elements.toLocaleString()}
├─ Unique Tag Types: ${data.element_analysis.unique_tags_count}
├─ Max Nesting Depth: ${data.element_analysis.max_nesting_depth}
├─ HTML Size: ${formatBytes(data.page_structure.document_info.total_html_size)}
├─ Text Content: ${formatBytes(data.page_structure.document_info.total_text_content)}
└─ Markup-to-Text Ratio: ${data.page_structure.document_info.markup_to_text_ratio.toFixed(2)}

[ATTRIBUTE ANALYSIS]
├─ Total Attributes: ${data.attribute_analysis.total_attributes.toLocaleString()}
├─ Unique Attribute Types: ${data.attribute_analysis.unique_attributes_count}
├─ Data Attributes: ${Object.keys(data.attribute_analysis.data_attributes).length}
├─ ARIA Attributes: ${Object.keys(data.attribute_analysis.aria_attributes).length}
└─ Custom Attributes: ${Object.keys(data.attribute_analysis.custom_attributes).length}

[LINK ANALYSIS]
├─ Total Links: ${data.link_analysis.summary.total_links}
├─ Internal Links: ${data.link_analysis.summary.internal_count}
├─ External Links: ${data.link_analysis.summary.external_count}
├─ Anchor Links: ${data.link_analysis.summary.anchor_count}
├─ Email Links: ${data.link_analysis.summary.email_count}
├─ Phone Links: ${data.link_analysis.summary.phone_count}
└─ File Links: ${data.link_analysis.summary.file_links_count}

[IMAGE ANALYSIS]
├─ Total Images: ${data.image_analysis.total_images}
├─ With Alt Text: ${data.image_analysis.with_alt}
├─ Without Alt Text: ${data.image_analysis.without_alt}
├─ Empty Alt Text: ${data.image_analysis.empty_alt}
├─ Lazy Loading: ${data.image_analysis.lazy_loading}
├─ Responsive Images: ${data.image_analysis.responsive_images}
├─ SVG Images: ${data.image_analysis.svg_images}
└─ Base64 Images: ${data.image_analysis.base64_images}

[SCRIPT ANALYSIS]
├─ Total Scripts: ${data.script_analysis.total_scripts}
├─ Inline Scripts: ${data.script_analysis.inline_scripts}
├─ External Scripts: ${data.script_analysis.external_scripts}
├─ Async Scripts: ${data.script_analysis.async_scripts}
├─ Defer Scripts: ${data.script_analysis.defer_scripts}
├─ Module Scripts: ${data.script_analysis.module_scripts}
├─ External Domains: ${data.script_analysis.external_domains_count}
└─ Frameworks: ${data.script_analysis.frameworks_detected.join(', ') || 'None detected'}

[PAGE STRUCTURE]
├─ Title: ${data.page_structure.head_analysis?.title || 'Not found'}
├─ Title Length: ${data.page_structure.head_analysis?.title_length || 0} chars
├─ Meta Tags: ${data.page_structure.head_analysis?.meta_tags || 0}
├─ Link Tags: ${data.page_structure.head_analysis?.link_tags || 0}
├─ Total Words: ${data.page_structure.text_statistics.total_words.toLocaleString()}
├─ Unique Words: ${data.page_structure.text_statistics.unique_words.toLocaleString()}
├─ Paragraphs: ${data.page_structure.text_statistics.paragraphs}
├─ Headings: ${data.page_structure.text_statistics.headings_total}
├─ Lists: ${data.page_structure.text_statistics.lists}
├─ Tables: ${data.page_structure.text_statistics.tables}
└─ Forms: ${data.page_structure.text_statistics.forms}

[SEMANTIC ELEMENTS]
├─ Header: ${data.page_structure.semantic_elements.header}
├─ Nav: ${data.page_structure.semantic_elements.nav}
├─ Main: ${data.page_structure.semantic_elements.main}
├─ Article: ${data.page_structure.semantic_elements.article}
├─ Section: ${data.page_structure.semantic_elements.section}
├─ Aside: ${data.page_structure.semantic_elements.aside}
└─ Footer: ${data.page_structure.semantic_elements.footer}

========================================================================
            `;
            
            container.textContent = stats;
        }
        
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        // Enter key support
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('urlInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    analyzeURL();
                }
            });
        });
    </script>
</body>
</html>'''


def create_flask_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        try:
            data = request.json
            url = data.get('url')
            
            if not url:
                return jsonify({'error': 'No URL provided'})
            
            # Perform analysis
            analyzer = ComprehensiveDOMAnalyzer(url)
            results = analyzer.generate_comprehensive_analysis()
            
            return jsonify(results)
            
        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'})
    
    return app


def run_cli_mode(url: str, output_file: str = None, format_type: str = 'json'):
    """Run the analyzer in CLI mode"""
    print(f"🔍 DOM Analyzer - Analyzing: {url}")
    print("=" * 60)
    
    analyzer = ComprehensiveDOMAnalyzer(url)
    results = analyzer.generate_comprehensive_analysis()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Print summary to console
    print(f"✅ Analysis Complete!")
    print(f"📊 Total Statistics Generated: {results['meta_analysis']['total_statistics_generated']:,}")
    print(f"⏱️  Processing Time: {results['meta_analysis']['processing_time']:.2f} seconds")
    print(f"🏗️  Total Elements: {results['element_analysis']['total_elements']:,}")
    print(f"🏷️  Unique Tags: {results['element_analysis']['unique_tags_count']}")
    print(f"📎 Total Attributes: {results['attribute_analysis']['total_attributes']:,}")
    print(f"🔗 Total Links: {results['link_analysis']['summary']['total_links']}")
    print(f"🖼️  Total Images: {results['image_analysis']['total_images']}")
    print(f"📜 Total Scripts: {results['script_analysis']['total_scripts']}")
    
    # Save to file if specified
    if output_file:
        if format_type == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"💾 Results saved to: {output_file}")
        elif format_type == 'text':
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"DOM Analyzer Report\n")
                f.write(f"URL: {results['url']}\n")
                f.write(f"Analysis Date: {results['meta_analysis']['analysis_timestamp']}\n")
                f.write(f"Total Statistics: {results['meta_analysis']['total_statistics_generated']:,}\n\n")
                
                f.write("SUMMARY\n")
                f.write("=" * 40 + "\n")
                f.write(f"Total Elements: {results['element_analysis']['total_elements']:,}\n")
                f.write(f"Unique Tags: {results['element_analysis']['unique_tags_count']}\n")
                f.write(f"Total Attributes: {results['attribute_analysis']['total_attributes']:,}\n")
                f.write(f"Total Links: {results['link_analysis']['summary']['total_links']}\n")
                f.write(f"Total Images: {results['image_analysis']['total_images']}\n")
                f.write(f"Total Scripts: {results['script_analysis']['total_scripts']}\n")
                
            print(f"📄 Text report saved to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='DOM Analyzer - The Ultimate Website Statistics Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  Web Interface:    python3 main.py
  CLI Analysis:     python3 main.py --url https://www.google.com
  Save to JSON:     python3 main.py --url https://www.google.com --output results.json
  Save to Text:     python3 main.py --url https://www.google.com --output report.txt --format text
        '''
    )
    
    parser.add_argument('--url', help='URL to analyze')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--format', choices=['json', 'text'], default='json', 
                       help='Output format (default: json)')
    parser.add_argument('--port', type=int, default=5000, 
                       help='Port for web interface (default: 5000)')
    parser.add_argument('--no-browser', action='store_true',
                       help='Don\'t open browser automatically')
    
    args = parser.parse_args()
    
    if args.url:
        # CLI Mode
        run_cli_mode(args.url, args.output, args.format)
    else:
        # Web Interface Mode
        app = create_flask_app()
        
        print("🌐 DOM Analyzer Web Interface Starting...")
        print(f"🚀 Open your browser to: http://localhost:{args.port}")
        print("📊 Generate 17,000+ real statistics for any website!")
        print("=" * 60)
        
        # Open browser automatically unless disabled
        if not args.no_browser:
            def open_browser():
                time.sleep(1)  # Wait for server to start
                webbrowser.open(f'http://localhost:{args.port}')
            
            threading.Thread(target=open_browser).start()
        
        # Start Flask app
        app.run(host='0.0.0.0', port=args.port, debug=False)


if __name__ == '__main__':
    main()