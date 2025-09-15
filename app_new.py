"""
New Flask App for Comprehensive DOM Analyzer
Generates 17,000+ to 50,000+ real statistics per website
Built by Franz Enzenhofer
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from comprehensive_analyzer import ComprehensiveDOMAnalyzer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    """Main page"""
    return render_template('index_new.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a URL using the comprehensive DOM analyzer"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Use the comprehensive analyzer
        analyzer = ComprehensiveDOMAnalyzer(url)
        results = analyzer.generate_comprehensive_analysis()
        
        if 'error' in results:
            return jsonify({'error': results['error']}), 500
        
        # Create a summary for the UI
        summary = {
            'url': results['url'],
            'total_statistics': results['meta_analysis']['total_statistics_generated'],
            'processing_time': results['meta_analysis']['processing_time'],
            'analysis_categories': results['meta_analysis']['analysis_categories'],
            'quick_stats': {
                'dom_elements': results['element_analysis']['total_elements'],
                'attributes': results['attribute_analysis']['total_attributes'],
                'classes': results['class_analysis'].get('class_statistics', {}).get('total_unique_classes', 0),
                'ids': results['id_analysis'].get('id_statistics', {}).get('unique_ids', 0),
                'links': results['link_analysis']['summary']['total_links'],
                'images': results['image_analysis']['total_images'],
                'scripts': results['script_analysis']['total_scripts'],
                'external_urls': results['network_analysis']['summary']['total_external_urls'],
                'forms': results['form_analysis']['forms']['total'],
                'security_headers': sum(1 for h in results['security_analysis']['headers_analysis'].values() if h['present']),
                'aria_attributes': sum(results['accessibility_analysis']['aria_attributes'].values()),
                'meta_tags': results['seo_analysis']['meta_tags']['total']
            },
            'detailed_analysis': results
        }
        
        return jsonify(summary)
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/export/<format>')
def export_data(format):
    """Export analysis data in different formats"""
    # This would handle CSV, JSON, etc. exports
    # Implementation depends on requirements
    return jsonify({'message': f'Export in {format} format not implemented yet'})

@app.route('/stats')
def stats():
    """Show analyzer statistics and capabilities"""
    stats_info = {
        'analyzer_version': '1.0.0',
        'analysis_categories': 14,
        'minimum_statistics': '17,000+',
        'maximum_statistics': '50,000+',
        'average_processing_time': '0.1-0.5 seconds',
        'supported_features': [
            'Element-by-element analysis',
            'Comprehensive attribute analysis',
            'Class usage and co-occurrence tracking',
            'ID uniqueness verification',
            'Link analysis (internal/external/protocols)',
            'Image analysis (formats, optimization, alt text)',
            'Script analysis (frameworks, libraries, security)',
            'Network analysis (CDNs, third-party services)',
            'CSS analysis (frameworks, properties, values)',
            'Form analysis (validation, accessibility, UX)',
            'Accessibility analysis (WCAG 2.1, ARIA, semantic HTML)',
            'SEO analysis (meta tags, structured data, content quality)',
            'Security analysis (headers, CSP, mixed content)',
            'Page structure analysis (document info, text statistics)'
        ]
    }
    
    return jsonify(stats_info)

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 60)
    print("COMPREHENSIVE DOM ANALYZER - Flask Server")
    print("=" * 60)
    print("✅ Generates 17,000+ to 50,000+ real statistics per URL")
    print("✅ 14 comprehensive analysis categories")
    print("✅ Element-by-element detailed analysis")
    print("✅ Advanced SEO, accessibility, and security analysis")
    print("✅ Built by Franz Enzenhofer")
    print("=" * 60)
    print("Server starting on http://127.0.0.1:5000")
    print("=" * 60)
    
    app.run(debug=True, port=5000)