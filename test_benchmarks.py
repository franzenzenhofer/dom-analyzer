"""
Performance Benchmarks for DOM Analyzer
Comprehensive performance testing and benchmarking suite
"""

import pytest
import time
import statistics
import psutil
import os
from typing import List, Dict, Any, Callable
import concurrent.futures
from dataclasses import dataclass
from contextlib import contextmanager
import threading
import json
import subprocess

from core_analyzer import CoreDOMAnalyzer
from test_fixtures import (
    MockHTMLFixtures, 
    TestDataGenerator,
    PerformanceBenchmarks
)
from bs4 import BeautifulSoup


@dataclass
class BenchmarkResult:
    """Benchmark result data structure"""
    name: str
    iterations: int
    times: List[float]
    memory_usage: List[float]
    success_rate: float
    average_time: float
    min_time: float
    max_time: float
    std_dev: float
    p95_time: float
    p99_time: float
    average_memory: float
    peak_memory: float


class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = None
        self.memory_samples = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start monitoring system resources"""
        self.initial_memory = self.process.memory_info().rss
        self.memory_samples = []
        self.monitoring = True
        
        def monitor():
            while self.monitoring:
                try:
                    current_memory = self.process.memory_info().rss
                    self.memory_samples.append(current_memory)
                    time.sleep(0.1)  # Sample every 100ms
                except:
                    break
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring and return results"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        if not self.memory_samples:
            return 0, 0
        
        memory_usage = [(sample - self.initial_memory) / 1024 / 1024 for sample in self.memory_samples]
        return statistics.mean(memory_usage), max(memory_usage)
    
    @contextmanager
    def monitoring(self):
        """Context manager for performance monitoring"""
        self.start_monitoring()
        try:
            yield self
        finally:
            avg_memory, peak_memory = self.stop_monitoring()
            self.last_avg_memory = avg_memory
            self.last_peak_memory = peak_memory


class BenchmarkRunner:
    """Run performance benchmarks"""
    
    def __init__(self):
        self.results = []
    
    def run_benchmark(
        self, 
        name: str, 
        func: Callable, 
        iterations: int = 10,
        *args, 
        **kwargs
    ) -> BenchmarkResult:
        """Run a benchmark function multiple times and collect metrics"""
        
        times = []
        memory_usage = []
        successes = 0
        
        print(f"Running benchmark: {name} ({iterations} iterations)")
        
        for i in range(iterations):
            monitor = PerformanceMonitor()
            
            with monitor.monitoring():
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    times.append(execution_time)
                    successes += 1
                    
                    print(f"  Iteration {i+1}/{iterations}: {execution_time:.3f}s")
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    times.append(execution_time)
                    print(f"  Iteration {i+1}/{iterations}: FAILED ({execution_time:.3f}s) - {str(e)[:50]}")
            
            memory_usage.append(monitor.last_avg_memory)
        
        # Calculate statistics
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            p95_time = sorted(times)[int(len(times) * 0.95)] if len(times) >= 2 else max_time
            p99_time = sorted(times)[int(len(times) * 0.99)] if len(times) >= 2 else max_time
        else:
            avg_time = min_time = max_time = std_dev = p95_time = p99_time = 0
        
        success_rate = successes / iterations
        avg_memory = statistics.mean(memory_usage) if memory_usage else 0
        peak_memory = max(memory_usage) if memory_usage else 0
        
        benchmark_result = BenchmarkResult(
            name=name,
            iterations=iterations,
            times=times,
            memory_usage=memory_usage,
            success_rate=success_rate,
            average_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            p95_time=p95_time,
            p99_time=p99_time,
            average_memory=avg_memory,
            peak_memory=peak_memory
        )
        
        self.results.append(benchmark_result)
        self._print_benchmark_summary(benchmark_result)
        
        return benchmark_result
    
    def _print_benchmark_summary(self, result: BenchmarkResult):
        """Print benchmark summary"""
        print(f"\n{result.name} Results:")
        print(f"  Success Rate: {result.success_rate:.1%}")
        print(f"  Average Time: {result.average_time:.3f}s")
        print(f"  Min/Max Time: {result.min_time:.3f}s / {result.max_time:.3f}s")
        print(f"  95th Percentile: {result.p95_time:.3f}s")
        print(f"  Standard Deviation: {result.std_dev:.3f}s")
        print(f"  Average Memory: {result.average_memory:.1f}MB")
        print(f"  Peak Memory: {result.peak_memory:.1f}MB")
        print()
    
    def export_results(self, filename: str):
        """Export results to JSON file"""
        export_data = []
        for result in self.results:
            export_data.append({
                'name': result.name,
                'iterations': result.iterations,
                'success_rate': result.success_rate,
                'average_time': result.average_time,
                'min_time': result.min_time,
                'max_time': result.max_time,
                'std_dev': result.std_dev,
                'p95_time': result.p95_time,
                'p99_time': result.p99_time,
                'average_memory': result.average_memory,
                'peak_memory': result.peak_memory,
                'times': result.times,
                'memory_usage': result.memory_usage
            })
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Results exported to {filename}")


class TestCoreFunctionBenchmarks:
    """Benchmark core analyzer functions"""
    
    @pytest.fixture(scope='class')
    def runner(self):
        """Benchmark runner fixture"""
        return BenchmarkRunner()
    
    @pytest.fixture(scope='class')
    def analyzer(self):
        """Core analyzer fixture"""
        return CoreDOMAnalyzer('https://example.com')
    
    def test_dom_complexity_simple_html(self, runner, analyzer):
        """Benchmark DOM complexity calculation with simple HTML"""
        soup = BeautifulSoup(MockHTMLFixtures.SIMPLE_HTML, 'html.parser')
        
        result = runner.run_benchmark(
            'DOM Complexity - Simple HTML',
            analyzer.calculate_dom_complexity,
            iterations=50,
            soup=soup
        )
        
        # Performance assertions
        assert result.success_rate >= 0.95
        assert result.average_time < 0.1  # Should be very fast for simple HTML
        assert result.average_memory < 10  # Low memory usage
    
    def test_dom_complexity_complex_html(self, runner, analyzer):
        """Benchmark DOM complexity calculation with complex HTML"""
        soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
        
        result = runner.run_benchmark(
            'DOM Complexity - Complex HTML',
            analyzer.calculate_dom_complexity,
            iterations=20,
            soup=soup
        )
        
        # Performance assertions
        assert result.success_rate >= 0.95
        assert result.average_time < 0.5  # Should complete quickly
        assert result.average_memory < 50  # Reasonable memory usage
    
    def test_dom_complexity_large_html(self, runner, analyzer):
        """Benchmark DOM complexity with large HTML"""
        large_html = TestDataGenerator.generate_large_html(1000)
        soup = BeautifulSoup(large_html, 'html.parser')
        
        result = runner.run_benchmark(
            'DOM Complexity - Large HTML (1000 elements)',
            analyzer.calculate_dom_complexity,
            iterations=10,
            soup=soup
        )
        
        # Performance assertions
        assert result.success_rate >= 0.9
        assert result.average_time < 2.0  # Should complete within 2 seconds
        assert result.average_memory < 100  # Memory should be reasonable
    
    def test_css_analysis_performance(self, runner, analyzer):
        """Benchmark CSS analysis performance"""
        soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
        
        result = runner.run_benchmark(
            'CSS Analysis - Complex HTML',
            analyzer.analyze_css_selectors,
            iterations=30,
            soup=soup
        )
        
        assert result.success_rate >= 0.95
        assert result.average_time < 0.2
        assert result.p95_time < 0.5
    
    def test_javascript_analysis_performance(self, runner, analyzer):
        """Benchmark JavaScript analysis performance"""
        soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
        
        result = runner.run_benchmark(
            'JavaScript Analysis - Complex HTML',
            analyzer.analyze_javascript_complexity,
            iterations=20,
            soup=soup
        )
        
        assert result.success_rate >= 0.95
        assert result.average_time < 0.3
    
    def test_seo_analysis_performance(self, runner, analyzer):
        """Benchmark SEO analysis performance"""
        soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
        
        result = runner.run_benchmark(
            'SEO Analysis - Complex HTML',
            analyzer.analyze_seo_signals,
            iterations=20,
            soup=soup
        )
        
        assert result.success_rate >= 0.95
        assert result.average_time < 0.5
        assert result.average_memory < 30
    
    def test_accessibility_analysis_performance(self, runner, analyzer):
        """Benchmark accessibility analysis performance"""
        soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
        
        result = runner.run_benchmark(
            'Accessibility Analysis - Complex HTML',
            analyzer.analyze_accessibility_advanced,
            iterations=20,
            soup=soup
        )
        
        assert result.success_rate >= 0.95
        assert result.average_time < 0.4
    
    def test_security_headers_performance(self, runner, analyzer):
        """Benchmark security headers analysis performance"""
        from test_fixtures import MockResponseFixtures
        headers = MockResponseFixtures.get_security_headers()
        
        result = runner.run_benchmark(
            'Security Headers Analysis',
            analyzer.analyze_security_headers,
            iterations=100,
            response_headers=headers
        )
        
        assert result.success_rate >= 0.99
        assert result.average_time < 0.01  # Should be very fast
    
    def test_statistics_counting_performance(self, runner, analyzer):
        """Benchmark statistics counting performance"""
        # Create a large nested dictionary
        large_data = {}
        for i in range(100):
            large_data[f'section_{i}'] = {
                f'subsection_{j}': {
                    f'key_{k}': f'value_{k}' for k in range(10)
                } for j in range(10)
            }
        
        result = runner.run_benchmark(
            'Statistics Counting - Large Dataset',
            analyzer.count_total_statistics,
            iterations=50,
            obj=large_data
        )
        
        assert result.success_rate >= 0.95
        assert result.average_time < 0.1
    
    @pytest.fixture(scope='class', autouse=True)
    def export_results(self, runner, request):
        """Export benchmark results after all tests"""
        yield
        runner.export_results('benchmark_results.json')


class TestScalabilityBenchmarks:
    """Test scalability with increasing load"""
    
    @pytest.fixture(scope='class')
    def runner(self):
        return BenchmarkRunner()
    
    @pytest.fixture(scope='class') 
    def analyzer(self):
        return CoreDOMAnalyzer('https://example.com')
    
    def test_scalability_by_dom_size(self, runner, analyzer):
        """Test performance scaling with DOM size"""
        sizes = [50, 100, 500, 1000, 2000]
        
        for size in sizes:
            html = TestDataGenerator.generate_large_html(size)
            soup = BeautifulSoup(html, 'html.parser')
            
            result = runner.run_benchmark(
                f'DOM Complexity - {size} elements',
                analyzer.calculate_dom_complexity,
                iterations=5,
                soup=soup
            )
            
            # Performance should degrade gracefully
            expected_max_time = 0.01 + (size * 0.001)  # Linear scaling expectation
            assert result.average_time < expected_max_time, f"Performance degraded too much for {size} elements"
    
    def test_scalability_by_depth(self, runner, analyzer):
        """Test performance scaling with nesting depth"""
        depths = [5, 10, 20, 50, 100]
        
        for depth in depths:
            html = TestDataGenerator.generate_deep_nested_html(depth)
            soup = BeautifulSoup(html, 'html.parser')
            
            result = runner.run_benchmark(
                f'DOM Complexity - Depth {depth}',
                analyzer.calculate_dom_complexity,
                iterations=10,
                soup=soup
            )
            
            # Should handle deep nesting efficiently
            assert result.success_rate >= 0.9
            assert result.average_time < 1.0  # Should complete within 1 second
    
    def test_concurrent_analysis_performance(self, runner, analyzer):
        """Test performance under concurrent load"""
        soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
        
        def concurrent_analysis():
            """Run multiple analyses concurrently"""
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                # Submit multiple analysis tasks
                for _ in range(5):
                    future = executor.submit(analyzer.calculate_dom_complexity, soup)
                    futures.append(future)
                
                # Wait for all to complete
                results = []
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result(timeout=10)
                        results.append(result)
                    except Exception as e:
                        print(f"Concurrent task failed: {e}")
                
                return len(results)
        
        result = runner.run_benchmark(
            'Concurrent Analysis (5 threads)',
            concurrent_analysis,
            iterations=5
        )
        
        assert result.success_rate >= 0.8  # Most should succeed
        assert result.average_time < 5.0  # Should complete reasonably fast


class TestMemoryBenchmarks:
    """Memory usage benchmarks"""
    
    @pytest.fixture(scope='class')
    def runner(self):
        return BenchmarkRunner()
    
    def test_memory_usage_scaling(self, runner):
        """Test memory usage with different HTML sizes"""
        sizes = [100, 500, 1000, 2000]
        
        def analyze_large_html(size):
            html = TestDataGenerator.generate_large_html(size)
            soup = BeautifulSoup(html, 'html.parser')
            analyzer = CoreDOMAnalyzer('https://example.com')
            
            # Run multiple analyses to test memory accumulation
            results = []
            for _ in range(3):
                result = analyzer.calculate_dom_complexity(soup)
                results.append(result)
            
            return results
        
        for size in sizes:
            result = runner.run_benchmark(
                f'Memory Usage - {size} elements',
                analyze_large_html,
                iterations=5,
                size=size
            )
            
            # Memory usage should be reasonable and not grow excessively
            max_acceptable_memory = size * 0.1  # 0.1 MB per 1000 elements
            assert result.peak_memory < max_acceptable_memory, f"Excessive memory usage for {size} elements"
    
    def test_memory_cleanup(self, runner):
        """Test memory cleanup after analysis"""
        def repeated_analysis():
            analyzer = CoreDOMAnalyzer('https://example.com')
            soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
            
            # Perform many analyses
            for _ in range(10):
                analyzer.calculate_dom_complexity(soup)
                analyzer.analyze_css_selectors(soup)
                analyzer.analyze_seo_signals(soup)
            
            # Force garbage collection
            import gc
            gc.collect()
            
            return True
        
        result = runner.run_benchmark(
            'Memory Cleanup Test',
            repeated_analysis,
            iterations=5
        )
        
        # Memory should not accumulate excessively
        assert result.average_memory < 50  # Less than 50MB average
        assert result.peak_memory < 100  # Less than 100MB peak


class TestRegressionBenchmarks:
    """Regression testing for performance"""
    
    @pytest.fixture(scope='class')
    def runner(self):
        return BenchmarkRunner()
    
    @pytest.fixture(scope='class')
    def analyzer(self):
        return CoreDOMAnalyzer('https://example.com')
    
    def test_performance_regression_baseline(self, runner, analyzer):
        """Establish performance baseline for regression testing"""
        soup = BeautifulSoup(MockHTMLFixtures.COMPLEX_HTML, 'html.parser')
        
        # Test all major functions
        functions = [
            ('DOM Complexity', analyzer.calculate_dom_complexity),
            ('CSS Analysis', analyzer.analyze_css_selectors),
            ('JavaScript Analysis', analyzer.analyze_javascript_complexity),
            ('SEO Analysis', analyzer.analyze_seo_signals),
            ('Accessibility Analysis', analyzer.analyze_accessibility_advanced),
        ]
        
        baseline_times = {}
        
        for name, func in functions:
            result = runner.run_benchmark(
                f'Baseline - {name}',
                func,
                iterations=20,
                soup=soup
            )
            
            baseline_times[name] = result.average_time
            
            # Store baseline for future regression tests
            # In a real scenario, you'd save this to a file or database
            print(f"Baseline {name}: {result.average_time:.3f}s")
        
        # All functions should complete within expected time bounds
        expected_max_times = {
            'DOM Complexity': 0.5,
            'CSS Analysis': 0.3,
            'JavaScript Analysis': 0.4,
            'SEO Analysis': 0.6,
            'Accessibility Analysis': 0.5,
        }
        
        for name, max_time in expected_max_times.items():
            assert baseline_times[name] < max_time, f"{name} exceeded expected baseline time"


def run_full_benchmark_suite():
    """Run complete benchmark suite"""
    print("="*60)
    print("DOM Analyzer Performance Benchmark Suite")
    print("="*60)
    
    # Use pytest to run benchmarks
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-x'  # Stop on first failure
    ])
    
    return exit_code


if __name__ == '__main__':
    run_full_benchmark_suite()