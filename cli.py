#!/usr/bin/env python3
"""
DOM Analyzer CLI - Command Line Interface
Uses the same core analyzer logic as the Flask app (DRY principle)
"""

import argparse
import json
import sys
import time
from typing import Dict, Any, Optional
from pathlib import Path

from core_analyzer import CoreDOMAnalyzer


class DOMAnalyzerCLI:
    """Command Line Interface for DOM Analysis"""
    
    def __init__(self):
        self.output_formats = ['json', 'summary', 'detailed', 'csv']
        self.user_agents = list(CoreDOMAnalyzer.USER_AGENTS.keys())
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser"""
        parser = argparse.ArgumentParser(
            description='DOM Analyzer CLI - Analyze web pages for SEO, performance, and accessibility',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com --format json --output results.json
  %(prog)s https://example.com --user-agent mobile_chrome --timeout 60
  %(prog)s https://example.com --format summary --categories seo performance
  %(prog)s https://example.com --benchmark --iterations 5
            """
        )
        
        # Required arguments
        parser.add_argument('url', help='URL to analyze')
        
        # Output options
        parser.add_argument(
            '--format', '-f',
            choices=self.output_formats,
            default='summary',
            help='Output format (default: summary)'
        )
        
        parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output file path (default: stdout)'
        )
        
        parser.add_argument(
            '--categories', '-c',
            nargs='+',
            choices=['dom', 'css', 'javascript', 'performance', 'seo', 'accessibility', 'security'],
            help='Specific analysis categories to include'
        )
        
        # Request options
        parser.add_argument(
            '--user-agent', '-u',
            choices=self.user_agents,
            default='desktop_chrome',
            help='User agent to use (default: desktop_chrome)'
        )
        
        parser.add_argument(
            '--timeout', '-t',
            type=int,
            default=30,
            help='Request timeout in seconds (default: 30)'
        )
        
        parser.add_argument(
            '--no-verify-ssl',
            action='store_true',
            help='Disable SSL certificate verification'
        )
        
        # Performance testing
        parser.add_argument(
            '--benchmark', '-b',
            action='store_true',
            help='Run performance benchmark'
        )
        
        parser.add_argument(
            '--iterations', '-i',
            type=int,
            default=3,
            help='Number of benchmark iterations (default: 3)'
        )
        
        # Utility options
        parser.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Suppress progress output'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Verbose output'
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version='DOM Analyzer CLI v1.0.0'
        )
        
        return parser
    
    def validate_url(self, url: str) -> str:
        """Validate and normalize URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def log(self, message: str, verbose_only: bool = False, quiet: bool = False):
        """Log message to stderr"""
        if quiet:
            return
        if verbose_only and not hasattr(self, 'verbose') or not self.verbose:
            return
        print(f"[CLI] {message}", file=sys.stderr)
    
    def run_single_analysis(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Run a single analysis"""
        self.log(f"Analyzing: {args.url}", quiet=args.quiet)
        
        # Create analyzer
        analyzer = CoreDOMAnalyzer(
            url=args.url,
            timeout=args.timeout,
            verify_ssl=not args.no_verify_ssl
        )
        
        # Run analysis
        start_time = time.time()
        results = analyzer.generate_comprehensive_analysis(user_agent=args.user_agent)
        analysis_time = time.time() - start_time
        
        # Add CLI metadata
        results['cli_metadata'] = {
            'analysis_time': analysis_time,
            'user_agent_used': args.user_agent,
            'timeout': args.timeout,
            'ssl_verification': not args.no_verify_ssl,
            'cli_version': '1.0.0'
        }
        
        self.log(f"Analysis completed in {analysis_time:.2f}s", quiet=args.quiet)
        
        return results
    
    def run_benchmark(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Run benchmark analysis"""
        self.log(f"Running benchmark with {args.iterations} iterations...", quiet=args.quiet)
        
        results = []
        times = []
        
        for i in range(args.iterations):
            self.log(f"Iteration {i+1}/{args.iterations}", verbose_only=True, quiet=args.quiet)
            
            start_time = time.time()
            result = self.run_single_analysis(args)
            iteration_time = time.time() - start_time
            
            results.append(result)
            times.append(iteration_time)
        
        # Calculate benchmark statistics
        benchmark_stats = {
            'iterations': args.iterations,
            'total_time': sum(times),
            'average_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'results': results
        }
        
        self.log(f"Benchmark completed. Avg: {benchmark_stats['average_time']:.2f}s", quiet=args.quiet)
        
        return benchmark_stats
    
    def filter_categories(self, results: Dict[str, Any], categories: list) -> Dict[str, Any]:
        """Filter results to include only specified categories"""
        if not categories:
            return results
        
        category_mapping = {
            'dom': 'dom_complexity',
            'css': 'css_analysis', 
            'javascript': 'javascript_analysis',
            'performance': 'performance_metrics',
            'seo': 'seo_signals',
            'accessibility': 'accessibility',
            'security': 'security'
        }
        
        filtered = {}
        
        # Always include metadata
        for key in ['url', 'user_agent_used', 'fetch_info', 'meta_statistics', 'cli_metadata']:
            if key in results:
                filtered[key] = results[key]
        
        # Include requested categories
        for category in categories:
            mapped_key = category_mapping.get(category, category)
            if mapped_key in results:
                filtered[mapped_key] = results[mapped_key]
        
        return filtered
    
    def format_json(self, data: Dict[str, Any], indent: int = 2) -> str:
        """Format as JSON"""
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    
    def format_summary(self, data: Dict[str, Any]) -> str:
        """Format as human-readable summary"""
        if 'error' in data:
            return f"Error: {data['error']}"
        
        lines = []
        lines.append(f"DOM Analysis Report")
        lines.append("=" * 50)
        lines.append(f"URL: {data.get('url', 'Unknown')}")
        lines.append(f"User Agent: {data.get('user_agent_used', 'Unknown')}")
        lines.append(f"Analysis Time: {data.get('cli_metadata', {}).get('analysis_time', 0):.2f}s")
        lines.append("")
        
        # Fetch info
        if 'fetch_info' in data:
            fetch = data['fetch_info']
            lines.append(f"Status Code: {fetch.get('status_code', 'N/A')}")
            lines.append(f"Content Length: {fetch.get('content_length', 0):,} bytes")
            lines.append(f"Response Time: {fetch.get('response_time', 0):.2f}s")
            lines.append("")
        
        # DOM Complexity
        if 'dom_complexity' in data:
            dom = data['dom_complexity']
            lines.append("DOM Complexity:")
            lines.append(f"  Total Elements: {dom.get('total_elements', 0):,}")
            lines.append(f"  Max Depth: {dom.get('max_depth', 0)}")
            lines.append(f"  Complexity Score: {dom.get('complexity_score', 0):,}")
            lines.append("")
        
        # SEO Signals
        if 'seo_signals' in data:
            seo = data['seo_signals']
            lines.append("SEO Analysis:")
            if 'title' in seo and seo['title'].get('exists'):
                title = seo['title']
                lines.append(f"  Title: '{title.get('text', 'N/A')[:60]}...'")
                lines.append(f"  Title Length: {title.get('length', 0)} chars ({'✓' if title.get('optimal') else '✗'} optimal)")
            
            if 'meta_tags' in seo and 'description' in seo['meta_tags'] and seo['meta_tags']['description'].get('exists'):
                desc = seo['meta_tags']['description']
                lines.append(f"  Meta Description Length: {desc.get('length', 0)} chars ({'✓' if desc.get('optimal') else '✗'} optimal)")
            
            if 'content_quality' in seo:
                content = seo['content_quality']
                lines.append(f"  Word Count: {content.get('word_count', 0):,}")
                lines.append(f"  Content-to-Code Ratio: {content.get('content_to_code_ratio', 0):.3f}")
            lines.append("")
        
        # Performance Metrics
        if 'performance_metrics' in data:
            perf = data['performance_metrics']
            lines.append("Performance:")
            if 'lazy_loading' in perf:
                lazy = perf['lazy_loading']
                lines.append(f"  Lazy Loaded Images: {lazy.get('images', 0)}")
            if 'image_optimization' in perf:
                img_opt = perf['image_optimization']
                lines.append(f"  Responsive Images: {img_opt.get('responsive_images', 0)}")
                lines.append(f"  Modern Image Formats: {img_opt.get('formats', {}).get('webp', 0)} WebP, {img_opt.get('formats', {}).get('avif', 0)} AVIF")
            lines.append("")
        
        # Accessibility
        if 'accessibility' in data:
            a11y = data['accessibility']
            lines.append("Accessibility:")
            if 'alternative_text' in a11y:
                alt = a11y['alternative_text']
                total_imgs = alt.get('total_images', 0)
                with_alt = alt.get('with_alt', 0)
                lines.append(f"  Images with Alt Text: {with_alt}/{total_imgs} ({(with_alt/total_imgs*100 if total_imgs > 0 else 0):.1f}%)")
            
            if 'form_labels' in a11y:
                forms = a11y['form_labels']
                with_labels = forms.get('inputs_with_labels', 0)
                without_labels = forms.get('inputs_without_labels', 0)
                total_inputs = with_labels + without_labels
                if total_inputs > 0:
                    lines.append(f"  Form Inputs with Labels: {with_labels}/{total_inputs} ({(with_labels/total_inputs*100):.1f}%)")
            lines.append("")
        
        # Security
        if 'security' in data:
            sec = data['security']
            lines.append("Security:")
            lines.append(f"  Security Score: {sec.get('security_score', 0):.1f}/100")
            lines.append(f"  HTTPS: {'✓' if data.get('url', '').startswith('https') else '✗'}")
            if 'csp' in sec:
                lines.append(f"  Content Security Policy: {'✓' if sec['csp'].get('present') else '✗'}")
            lines.append("")
        
        # Meta Statistics
        if 'meta_statistics' in data:
            meta = data['meta_statistics']
            lines.append("Analysis Summary:")
            lines.append(f"  Total Data Points: {meta.get('total_data_points', 0):,}")
            lines.append(f"  Analysis Categories: {meta.get('analysis_categories', 0)}")
            lines.append(f"  Processing Time: {meta.get('processing_time', 0):.2f}s")
            lines.append(f"  Timestamp: {meta.get('timestamp', 'N/A')}")
        
        return "\n".join(lines)
    
    def format_detailed(self, data: Dict[str, Any]) -> str:
        """Format as detailed report"""
        return self.format_json(data, indent=2)
    
    def format_csv(self, data: Dict[str, Any]) -> str:
        """Format key metrics as CSV"""
        if 'error' in data:
            return f"url,error\n{data.get('url', '')},{data['error']}"
        
        # Extract key metrics
        metrics = {
            'url': data.get('url', ''),
            'status_code': data.get('fetch_info', {}).get('status_code', ''),
            'content_length': data.get('fetch_info', {}).get('content_length', ''),
            'response_time': data.get('fetch_info', {}).get('response_time', ''),
            'total_elements': data.get('dom_complexity', {}).get('total_elements', ''),
            'max_depth': data.get('dom_complexity', {}).get('max_depth', ''),
            'title_length': data.get('seo_signals', {}).get('title', {}).get('length', ''),
            'word_count': data.get('seo_signals', {}).get('content_quality', {}).get('word_count', ''),
            'images_with_alt': data.get('accessibility', {}).get('alternative_text', {}).get('with_alt', ''),
            'total_images': data.get('accessibility', {}).get('alternative_text', {}).get('total_images', ''),
            'security_score': data.get('security', {}).get('security_score', ''),
            'processing_time': data.get('meta_statistics', {}).get('processing_time', '')
        }
        
        # Create CSV
        headers = ','.join(metrics.keys())
        values = ','.join(str(v) for v in metrics.values())
        
        return f"{headers}\n{values}"
    
    def save_output(self, content: str, output_path: str):
        """Save content to file"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"Results saved to: {output_path}")
        except Exception as e:
            self.log(f"Error saving to {output_path}: {e}")
            sys.exit(1)
    
    def run(self):
        """Main CLI runner"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        # Store verbose setting
        self.verbose = args.verbose
        
        # Validate and normalize URL
        args.url = self.validate_url(args.url)
        
        try:
            # Run analysis
            if args.benchmark:
                results = self.run_benchmark(args)
            else:
                results = self.run_single_analysis(args)
            
            # Filter categories if specified
            if args.categories and not args.benchmark:
                results = self.filter_categories(results, args.categories)
            
            # Format output
            formatters = {
                'json': self.format_json,
                'summary': self.format_summary,
                'detailed': self.format_detailed,
                'csv': self.format_csv
            }
            
            formatter = formatters[args.format]
            output = formatter(results)
            
            # Save or print output
            if args.output:
                self.save_output(output, args.output)
            else:
                print(output)
        
        except KeyboardInterrupt:
            self.log("Analysis cancelled by user")
            sys.exit(1)
        except Exception as e:
            self.log(f"Error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)


def main():
    """CLI entry point"""
    cli = DOMAnalyzerCLI()
    cli.run()


if __name__ == '__main__':
    main()