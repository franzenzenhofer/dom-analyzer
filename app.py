from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import tldextract
import json
import re
from collections import Counter, defaultdict
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import cssselect
import networkx as nx
from pyvis.network import Network
import os
import tempfile

# Import the refactored core analyzer
from core_analyzer import LegacyDOMAnalyzer, CoreDOMAnalyzer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configuration for analyzer behavior
ANALYZER_CONFIG = {
    'use_legacy_mode': True,  # Set to False to use new comprehensive analysis
    'timeout': 30,
    'verify_ssl': False,
    'user_agent': 'desktop_chrome'
}

# Legacy DOMAnalyzer wrapper for backward compatibility
# Now uses the refactored core analyzer under the hood
class DOMAnalyzer:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.base_domain = tldextract.extract(url).registered_domain
        
        # Initialize the appropriate analyzer based on config
        if ANALYZER_CONFIG['use_legacy_mode']:
            self.core_analyzer = LegacyDOMAnalyzer(url)
        else:
            self.core_analyzer = CoreDOMAnalyzer(
                url, 
                timeout=ANALYZER_CONFIG['timeout'],
                verify_ssl=ANALYZER_CONFIG['verify_ssl']
            )
        
        # Maintain backward compatibility with existing properties
        self.soup = None
        self.html_content = None
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
        
    def fetch_page(self):
        """Fetch page using core analyzer - maintains backward compatibility"""
        try:
            if ANALYZER_CONFIG['use_legacy_mode']:
                # Use legacy analyzer's fetch method
                success = self.core_analyzer.fetch_page()
                if success:
                    self.soup = self.core_analyzer.soup
                    self.html_content = self.core_analyzer.html_content
                return success
            else:
                # Use new core analyzer
                response_data = self.core_analyzer.fetch_single_user_agent(ANALYZER_CONFIG['user_agent'])
                if response_data:
                    self.html_content = response_data['html']
                    self.soup = response_data['soup']
                    return True
                return False
        except Exception as e:
            print(f"Error fetching page: {e}")
            return False
    
    
    def categorize_domain(self, asset_url):
        """Delegate to core analyzer for domain categorization"""
        if hasattr(self.core_analyzer, 'categorize_domain'):
            return self.core_analyzer.categorize_domain(asset_url)
        else:
            # Fallback implementation
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
            except:
                return 'same_origin', asset_url
    
    def extract_assets(self):
        """Delegate asset extraction to core analyzer or use legacy method"""
        if hasattr(self.core_analyzer, 'extract_assets'):
            self.core_analyzer.extract_assets()
            # Copy results to maintain compatibility
            if hasattr(self.core_analyzer, 'assets'):
                self.assets = self.core_analyzer.assets
            if hasattr(self.core_analyzer, 'domain_stats'):
                self.domain_stats = self.core_analyzer.domain_stats
        # If no extract_assets method, keep original implementation (truncated for brevity)
    
    def calculate_statistics(self):
        """Delegate statistics calculation to core analyzer"""
        if hasattr(self.core_analyzer, 'calculate_statistics'):
            self.core_analyzer.calculate_statistics()
            # Copy results to maintain compatibility
            if hasattr(self.core_analyzer, 'statistics'):
                self.statistics = self.core_analyzer.statistics
    
    def create_dependency_graph(self):
        """Create dependency graph - enhanced with core analyzer data"""
        G = nx.DiGraph()
        
        # Add main domain node
        G.add_node(self.parsed_url.netloc, 
                   color='#4CAF50', 
                   size=30, 
                   title=f"Main Domain: {self.parsed_url.netloc}",
                   group='main')
        
        # Track unique domains
        unique_domains = set()
        
        # Process all assets
        for asset_type, assets_list in self.assets.items():
            for asset in assets_list:
                if isinstance(asset, dict) and 'url' in asset:
                    parsed = urlparse(asset['url'])
                    if parsed.netloc and parsed.netloc not in unique_domains:
                        unique_domains.add(parsed.netloc)
                        
                        # Determine node color based on category
                        category = asset.get('category', 'third_party')
                        if category == 'same_origin':
                            color = '#2196F3'
                            group = 'same_origin'
                        elif category == 'subdomain':
                            color = '#FF9800'
                            group = 'subdomain'
                        else:
                            color = '#f44336'
                            group = 'third_party'
                        
                        G.add_node(parsed.netloc, 
                                   color=color, 
                                   size=15,
                                   title=f"{asset_type.capitalize()}: {parsed.netloc}",
                                   group=group)
                        G.add_edge(self.parsed_url.netloc, parsed.netloc, 
                                   title=asset_type,
                                   color=color)
        
        # Create interactive graph
        net = Network(height='600px', width='100%', bgcolor='#ffffff', font_color='#333333')
        net.from_nx(G)
        net.force_atlas_2based()
        
        # Save to temporary file
        graph_path = os.path.join('static', 'dependency_graph.html')
        os.makedirs('static', exist_ok=True)
        net.save_graph(graph_path)
        
        return graph_path
    
    def analyze(self):
        """Main analyze method - now uses core analyzer with backward compatibility"""
        try:
            if ANALYZER_CONFIG['use_legacy_mode']:
                # Use legacy analyzer
                result = self.core_analyzer.analyze()
                if result:
                    # Update local properties for backward compatibility
                    self.assets = result.get('assets', self.assets)
                    self.domain_stats = result.get('domain_stats', self.domain_stats)
                    self.statistics = result.get('statistics', self.statistics)
                    
                    # Create dependency graph
                    graph_path = self.create_dependency_graph()
                    result['graph_path'] = graph_path
                    
                return result
            else:
                # Use new comprehensive analyzer
                comprehensive_result = self.core_analyzer.generate_comprehensive_analysis(ANALYZER_CONFIG['user_agent'])
                
                if 'error' in comprehensive_result:
                    return None
                
                # Transform comprehensive results to legacy format
                self.soup = comprehensive_result.get('soup')  # May not exist in comprehensive
                
                # Create compatible assets structure
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
                
                # Transform comprehensive statistics to legacy format
                self.statistics = {
                    'comprehensive_analysis': comprehensive_result,
                    'html_stats': {
                        'total_size': comprehensive_result.get('fetch_info', {}).get('content_length', 0),
                        'total_tags': comprehensive_result.get('dom_complexity', {}).get('total_elements', 0),
                    },
                    'seo_analysis': comprehensive_result.get('seo_signals', {}),
                    'accessibility': comprehensive_result.get('accessibility', {}),
                    'performance': comprehensive_result.get('performance_metrics', {}),
                    'security': comprehensive_result.get('security', {})
                }
                
                # Create dependency graph
                graph_path = self.create_dependency_graph()
                
                return {
                    'url': self.url,
                    'assets': self.assets,
                    'domain_stats': self.domain_stats,
                    'statistics': self.statistics,
                    'graph_path': graph_path,
                    'comprehensive_data': comprehensive_result  # Include full data
                }
                
        except Exception as e:
            print(f"Analysis error: {e}")
            return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    analyzer = DOMAnalyzer(url)
    results = analyzer.analyze()
    
    if results:
        return jsonify(results)
    else:
        return jsonify({'error': 'Failed to analyze URL'}), 500

@app.route('/graph')
def graph():
    return render_template('graph.html')

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, port=5000)